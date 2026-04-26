import json
import uuid
from datetime import datetime, timedelta

from extensions import db
from models.answer import AnswerRecord
from models.diary import DiaryEntry
from models.mood_analysis_job import MoodAnalysisJob
from models.user_profile import UserProfile
from services import content_generation_service


class ProfileAnalysisService:
    ANALYSIS_COOLDOWN_HOURS = 1

    @staticmethod
    def _build_request_id(user_id: str, trigger_event: str, event_time: datetime):
        raw = f'{user_id}:{trigger_event}:{event_time.strftime("%Y%m%d%H%M")}'
        return str(uuid.uuid5(uuid.NAMESPACE_URL, raw))

    @staticmethod
    def enqueue_analysis(
        user_id: str,
        trigger_event: str,
        event_time: datetime,
        payload: dict | None = None,
        window_days: int = 7,
    ):
        if not user_id:
            raise ValueError('user_id is required')
        if not trigger_event:
            raise ValueError('trigger_event is required')
        if not isinstance(event_time, datetime):
            raise ValueError('event_time must be a datetime')

        request_id = ProfileAnalysisService._build_request_id(user_id, trigger_event, event_time)
        existing = MoodAnalysisJob.query.filter_by(request_id=request_id).first()
        if existing:
            return existing

        job = MoodAnalysisJob(
            id=str(uuid.uuid4()),
            user_id=user_id,
            status='pending',
            trigger_event=trigger_event,
            window_days=window_days,
            payload_json=payload or {},
            request_id=request_id,
            next_run_at=datetime.utcnow(),
        )
        db.session.add(job)
        db.session.commit()
        return job

    @staticmethod
    def pick_next_job(now: datetime | None = None):
        current = now or datetime.utcnow()
        return MoodAnalysisJob.query.filter(
            MoodAnalysisJob.status == 'pending',
            MoodAnalysisJob.next_run_at <= current,
        ).order_by(MoodAnalysisJob.created_at.asc()).first()

    @staticmethod
    def _need_analysis(user_id: str) -> bool:
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile or not profile.updated_at:
            return True
        return (datetime.utcnow() - profile.updated_at).total_seconds() > ProfileAnalysisService.ANALYSIS_COOLDOWN_HOURS * 3600

    @staticmethod
    def analyze_profile_with_llm(user_id: str, window_days: int) -> dict:
        window_start = datetime.utcnow() - timedelta(days=window_days)

        diary_entries = DiaryEntry.query.filter(
            DiaryEntry.user_id == user_id,
            DiaryEntry.created_at >= window_start,
        ).order_by(DiaryEntry.created_at.desc()).limit(20).all()

        answer_records = AnswerRecord.query.filter(
            AnswerRecord.user_id == user_id,
            AnswerRecord.created_at >= window_start,
        ).order_by(AnswerRecord.created_at.desc()).limit(20).all()

        provider = content_generation_service.get_provider()
        result = provider.analyze_user_profile(
            diary_entries=[{
                "mood_tag": e.mood_tag.value if hasattr(e.mood_tag, 'value') else str(e.mood_tag),
                "content": e.content or "",
            } for e in diary_entries],
            answer_questions=[{
                "question": a.question or "",
            } for a in answer_records],
        )

        return result

    @staticmethod
    def apply_ai_analysis_result(user_id: str, result: dict):
        if not isinstance(result, dict):
            raise ValueError('result must be a dict')

        mood_tendency = result.get('mood_tendency', '').strip()
        if not mood_tendency:
            raise ValueError('mood_tendency must be non-empty')

        topic_interests = result.get('topic_interests', [])
        if not isinstance(topic_interests, list):
            topic_interests = []

        self_context_tag = (result.get('self_context_tag') or '').strip()[:20]

        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = UserProfile(
                user_id=user_id,
                topic_interests=[],
                personalization_enabled=True,
            )
            db.session.add(profile)

        profile.mood_tendency = mood_tendency[:50]
        profile.topic_interests = topic_interests
        profile.self_context_tag = self_context_tag
        db.session.flush()
        return profile

    @staticmethod
    def trigger_analysis_if_needed(user_id: str, window_days: int = 7):
        if not ProfileAnalysisService._need_analysis(user_id):
            return None
        result = ProfileAnalysisService.analyze_profile_with_llm(user_id, window_days)
        profile = ProfileAnalysisService.apply_ai_analysis_result(user_id, result)
        db.session.commit()
        return profile

    @staticmethod
    def process_one_job(now: datetime | None = None):
        job = ProfileAnalysisService.pick_next_job(now=now)
        if not job:
            return None

        job.status = 'running'
        job.started_at = datetime.utcnow()
        job.attempt_count += 1
        db.session.flush()

        try:
            result = ProfileAnalysisService.analyze_profile_with_llm(
                user_id=job.user_id,
                window_days=job.window_days,
            )
            ProfileAnalysisService.apply_ai_analysis_result(job.user_id, result)
            job.status = 'succeeded'
            job.result_text = json.dumps(result, ensure_ascii=False)[:64]
            job.finished_at = datetime.utcnow()
            job.error_message = None
            db.session.commit()
            return job
        except Exception as exc:
            if job.attempt_count >= job.max_attempts:
                job.status = 'failed_terminal'
                job.next_run_at = datetime.utcnow()
            else:
                job.status = 'pending'
                delay = 1 if job.attempt_count == 1 else 5 if job.attempt_count == 2 else 30
                job.next_run_at = datetime.utcnow() + timedelta(minutes=delay)
            job.error_message = str(exc)[:255]
            job.finished_at = datetime.utcnow()
            db.session.commit()
            return job

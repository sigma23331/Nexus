from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models.answer import AnswerRecord
from models.diary import DiaryEntry
from models.fortune import FortuneRecord
from models.user_profile import (
    ActiveHourBucket,
    AnswerStyle,
    MoodTendency,
    PreferredFeature,
    UserProfile,
)


class UserProfileService:
    @staticmethod
    def _validate_window_days(window_days: int):
        if isinstance(window_days, bool) or not isinstance(window_days, int):
            raise ValueError('window_days must be an integer')
        if window_days <= 0:
            raise ValueError('window_days must be greater than 0')

    @staticmethod
    def _window_start(days: int, now: datetime | None = None):
        UserProfileService._validate_window_days(days)
        current = now or datetime.utcnow()
        return current - timedelta(days=days)

    @staticmethod
    def get_by_user_id(user_id: str):
        return UserProfile.query.filter_by(user_id=user_id).first()

    @staticmethod
    def get_or_create_profile(user_id: str):
        profile = UserProfileService.get_by_user_id(user_id)
        if profile:
            return profile

        profile = UserProfile(
            user_id=user_id,
            topic_interests=[],
            personalization_enabled=True,
        )
        db.session.add(profile)
        db.session.flush()
        return profile

    @staticmethod
    def calc_preferred_feature_in_window(
        user_id: str,
        window_days: int,
        now: datetime | None = None,
    ):
        window_start = UserProfileService._window_start(days=window_days, now=now)

        diary_count, diary_latest = db.session.query(
            func.count(DiaryEntry.id),
            func.max(DiaryEntry.created_at),
        ).filter(
            DiaryEntry.user_id == user_id,
            DiaryEntry.created_at >= window_start,
        ).one()

        fortune_count, fortune_latest = db.session.query(
            func.count(FortuneRecord.id),
            func.max(FortuneRecord.created_at),
        ).filter(
            FortuneRecord.user_id == user_id,
            FortuneRecord.created_at >= window_start,
        ).one()

        answer_count, answer_latest = db.session.query(
            func.count(AnswerRecord.id),
            func.max(AnswerRecord.created_at),
        ).filter(
            AnswerRecord.user_id == user_id,
            AnswerRecord.created_at >= window_start,
        ).one()

        candidates = [
            {
                'feature': PreferredFeature.MOOD_DIARY,
                'count': diary_count or 0,
                'latest': diary_latest,
            },
            {
                'feature': PreferredFeature.FORTUNE,
                'count': fortune_count or 0,
                'latest': fortune_latest,
            },
            {
                'feature': PreferredFeature.ANSWER,
                'count': answer_count or 0,
                'latest': answer_latest,
            },
        ]

        max_count = max(item['count'] for item in candidates)
        if max_count == 0:
            return None

        top_candidates = [item for item in candidates if item['count'] == max_count]
        top_candidates.sort(
            key=lambda item: item['latest'] or datetime.min,
            reverse=True,
        )
        return top_candidates[0]['feature']

    @staticmethod
    def calc_active_hour_bucket_in_window(
        user_id: str,
        window_days: int,
        now: datetime | None = None,
    ):
        window_start = UserProfileService._window_start(days=window_days, now=now)

        timestamps = []
        timestamps.extend(
            created_at for (created_at,) in db.session.query(DiaryEntry.created_at).filter(
                DiaryEntry.user_id == user_id,
                DiaryEntry.created_at >= window_start,
            ).all() if created_at
        )
        timestamps.extend(
            created_at for (created_at,) in db.session.query(FortuneRecord.created_at).filter(
                FortuneRecord.user_id == user_id,
                FortuneRecord.created_at >= window_start,
            ).all() if created_at
        )
        timestamps.extend(
            created_at for (created_at,) in db.session.query(AnswerRecord.created_at).filter(
                AnswerRecord.user_id == user_id,
                AnswerRecord.created_at >= window_start,
            ).all() if created_at
        )

        if not timestamps:
            return None

        hour_counter = Counter(ts.hour for ts in timestamps)
        latest_ts_by_hour = {}
        for ts in timestamps:
            current_latest = latest_ts_by_hour.get(ts.hour)
            if not current_latest or ts > current_latest:
                latest_ts_by_hour[ts.hour] = ts

        top_hour = sorted(
            hour_counter.items(),
            key=lambda item: (item[1], latest_ts_by_hour[item[0]]),
            reverse=True,
        )[0][0]

        if 6 <= top_hour <= 11:
            return ActiveHourBucket.MORNING
        if 12 <= top_hour <= 17:
            return ActiveHourBucket.AFTERNOON
        return ActiveHourBucket.NIGHT

    @staticmethod
    def recompute_rule_profile_fields_in_window(
        user_id: str,
        window_days: int,
        now: datetime | None = None,
    ):
        preferred_feature = UserProfileService.calc_preferred_feature_in_window(
            user_id,
            window_days=window_days,
            now=now,
        )
        active_hour_bucket = UserProfileService.calc_active_hour_bucket_in_window(
            user_id,
            window_days=window_days,
            now=now,
        )

        update_data = {}
        if preferred_feature is not None:
            update_data['preferred_feature'] = preferred_feature
        if active_hour_bucket is not None:
            update_data['active_hour_bucket'] = active_hour_bucket

        return update_data

    @staticmethod
    def update_profile_by_behavior(
        user_id: str,
        event_type: str,
        event_time: datetime,
        payload: dict | None = None,
        window_days: int = 7,
    ):
        if not user_id:
            raise ValueError('user_id is required')
        if not event_type:
            raise ValueError('event_type is required')
        if not isinstance(event_time, datetime):
            raise ValueError('event_time must be a datetime')

        profile = UserProfileService.get_or_create_profile(user_id)
        update_data = UserProfileService.recompute_rule_profile_fields_in_window(
            user_id=user_id,
            window_days=window_days,
            now=event_time,
        )

        changed_data = {}
        for key, value in update_data.items():
            if getattr(profile, key) != value:
                changed_data[key] = value

        if changed_data:
            for key, value in changed_data.items():
                setattr(profile, key, value)

        db.session.commit()
        return profile

    @staticmethod
    def create(user_id: str, **kwargs):
        profile = UserProfile(user_id=user_id, **kwargs)
        db.session.add(profile)
        db.session.commit()
        return profile

    @staticmethod
    def update(user_id: str, **kwargs):
        profile = UserProfileService.get_by_user_id(user_id)
        if not profile:
            return None

        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        db.session.commit()
        return profile

    @staticmethod
    def to_dict(profile: UserProfile):
        if not profile:
            return None

        return {
            'user_id': profile.user_id,
            'answer_style': profile.answer_style.value if profile.answer_style else None,
            'topic_interests': profile.topic_interests or [],
            'self_context_tag': profile.self_context_tag,
            'mood_tendency': profile.mood_tendency.value if profile.mood_tendency else None,
            'preferred_feature': profile.preferred_feature.value if profile.preferred_feature else None,
            'active_hour_bucket': profile.active_hour_bucket.value if profile.active_hour_bucket else None,
            'personalization_enabled': profile.personalization_enabled,
            'created_at': profile.created_at.isoformat() if profile.created_at else None,
            'updated_at': profile.updated_at.isoformat() if profile.updated_at else None,
        }

    @staticmethod
    def parse_update_payload(payload: dict):
        allowed_fields = {
            'answer_style',
            'topic_interests',
            'self_context_tag',
            'mood_tendency',
            'preferred_feature',
            'active_hour_bucket',
            'personalization_enabled',
        }

        enum_maps = {
            'answer_style': AnswerStyle,
            'mood_tendency': MoodTendency,
            'preferred_feature': PreferredFeature,
            'active_hour_bucket': ActiveHourBucket,
        }

        update_data = {}

        for key, value in payload.items():
            if key not in allowed_fields:
                continue

            if key in enum_maps:
                if value is None:
                    update_data[key] = None
                    continue

                try:
                    update_data[key] = enum_maps[key](value)
                except ValueError as exc:
                    raise ValueError(f'Invalid value for {key}: {value}') from exc
                continue

            if key == 'topic_interests':
                if value is None:
                    update_data[key] = []
                elif isinstance(value, list):
                    update_data[key] = value
                else:
                    raise ValueError('topic_interests must be a list')
                continue

            if key == 'personalization_enabled':
                if not isinstance(value, bool):
                    raise ValueError('personalization_enabled must be a boolean')
                update_data[key] = value
                continue

            update_data[key] = value

        return update_data

    @staticmethod
    def create_default_profile(session, user_id: str):
        profile = UserProfile(
            user_id=user_id,
            topic_interests=[],
            personalization_enabled=True,
        )
        session.add(profile)
        return profile

    @staticmethod
    def safe_update(user_id: str, **kwargs):
        try:
            profile = UserProfileService.update(user_id, **kwargs)
            return profile, None
        except SQLAlchemyError as exc:
            db.session.rollback()
            return None, str(exc)

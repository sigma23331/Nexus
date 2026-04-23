from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models.user_profile import (
    ActiveHourBucket,
    AnswerStyle,
    MoodTendency,
    PreferredFeature,
    UserProfile,
)


class UserProfileService:
    @staticmethod
    def get_by_user_id(user_id: str):
        return UserProfile.query.filter_by(user_id=user_id).first()

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

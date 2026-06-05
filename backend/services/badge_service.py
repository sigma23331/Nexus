from collections import defaultdict
from datetime import date, datetime, timedelta

from sqlalchemy.exc import IntegrityError

from extensions import db
from models.answer import AnswerRecord
from models.association import Favorite, Like
from models.badge import BadgeDefinition, UserBadge, UserBadgeNotification, UserLoginDay
from models.diary import DiaryEntry
from models.fortune import FortuneRecord
from models.plaza import PlazaCard
from models.plaza_comment import PlazaComment
from services.badge_catalog import BADGE_CATALOG


LUCKY_SCORE_THRESHOLD = 90

TRIGGER_BADGE_CODES = {
    "fortune_created": {"first_fortune", "lucky_streak", "fortune_companion"},
    "diary_created": {"diary_writer"},
    "answer_created": {"answer_traveler"},
    "favorite_changed": {"favorite_collector"},
    "plaza_card_created": {"share_station"},
    "plaza_interaction_changed": {"social_master"},
    "login": {"login_streak"},
}


def _fallback_definitions():
    return [
        {
            **item,
            "icon_url": f"/images/badges/{item['code']}.png",
            "gray_icon_url": f"/images/badges/{item['code']}_gray.png",
            "enabled": True,
        }
        for item in BADGE_CATALOG
    ]


def _format_level(level):
    if isinstance(level, dict):
        return dict(level)
    return {
        "level": level.level,
        "title": level.title,
        "condition_type": level.condition_type,
        "metric_key": level.metric_key,
        "threshold": level.threshold,
        "description": level.description,
    }


def _format_definition(definition):
    if isinstance(definition, dict):
        levels = [_format_level(level) for level in definition["levels"]]
        return {**definition, "levels": sorted(levels, key=lambda item: item["level"])}
    levels = [_format_level(level) for level in definition.levels]
    return {
        "code": definition.code,
        "name": definition.name,
        "category": definition.category,
        "description": definition.description,
        "icon_url": definition.icon_url,
        "gray_icon_url": definition.gray_icon_url,
        "sort_order": definition.sort_order,
        "enabled": definition.enabled,
        "levels": sorted(levels, key=lambda item: item["level"]),
    }


def _active_definitions(badge_codes=None):
    query = BadgeDefinition.query.filter_by(enabled=True).order_by(BadgeDefinition.sort_order.asc())
    if badge_codes:
        query = query.filter(BadgeDefinition.code.in_(badge_codes))
    rows = query.all()
    if rows:
        return [_format_definition(row) for row in rows]

    fallback = _fallback_definitions()
    if badge_codes:
        fallback = [item for item in fallback if item["code"] in badge_codes]
    return fallback


def list_definitions():
    return {"list": [_public_definition_payload(definition) for definition in _active_definitions()]}


def record_login_day(user_id, login_date=None):
    login_date = login_date or date.today()
    exists = UserLoginDay.query.filter_by(user_id=user_id, login_date=login_date).first()
    if exists:
        return {"created": False, "loginDate": login_date.isoformat()}

    db.session.add(UserLoginDay(user_id=user_id, login_date=login_date))
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"created": False, "loginDate": login_date.isoformat()}
    return {"created": True, "loginDate": login_date.isoformat()}


def record_login_and_evaluate(user_id, login_date=None):
    try:
        record_login_day(user_id=user_id, login_date=login_date)
        return evaluate_user_badges(user_id=user_id, trigger="login")
    except Exception:
        _safe_rollback()
        return {"newUnlocks": [], "upgrades": [], "failed": True}


def evaluate_after_event(user_id, trigger):
    try:
        return evaluate_user_badges(user_id=user_id, trigger=trigger)
    except Exception:
        _safe_rollback()
        return {"newUnlocks": [], "upgrades": [], "failed": True}


def _safe_rollback():
    try:
        db.session.rollback()
    except Exception:
        pass


def evaluate_user_badges(user_id, trigger=None):
    badge_codes = TRIGGER_BADGE_CODES.get(trigger) if trigger else None
    definitions = _active_definitions(badge_codes)
    if not definitions:
        return {"newUnlocks": [], "upgrades": []}

    metric_keys = {level["metric_key"] for definition in definitions for level in definition["levels"]}
    metrics = collect_metrics(user_id=user_id, metric_keys=metric_keys)
    existing = {
        row.badge_code: row
        for row in UserBadge.query.filter(
            UserBadge.user_id == user_id,
            UserBadge.badge_code.in_([item["code"] for item in definitions]),
        ).all()
    }

    new_unlocks = []
    upgrades = []
    for definition in definitions:
        result = _evaluate_definition(definition, metrics)
        previous = existing.get(definition["code"])
        previous_level = previous.level if previous else 0
        row = _upsert_user_badge(user_id=user_id, definition=definition, result=result, existing=previous)
        if result["level"] > previous_level:
            payload = _format_user_badge(definition, row)
            if previous_level <= 0:
                new_unlocks.append(payload)
                _create_badge_notification(user_id, definition["code"], result["level"], "unlock")
            else:
                upgrades.append(payload)
                _create_badge_notification(user_id, definition["code"], result["level"], "upgrade")

    db.session.commit()
    return {"newUnlocks": new_unlocks, "upgrades": upgrades}


def list_user_badges(user_id):
    evaluate_user_badges(user_id=user_id)
    definitions = _active_definitions()
    rows = {row.badge_code: row for row in UserBadge.query.filter_by(user_id=user_id).all()}
    items = [_format_user_badge(definition, rows.get(definition["code"])) for definition in definitions]
    return {
        "unlockedCount": sum(1 for item in items if item["unlocked"]),
        "totalCount": len(items),
        "list": items,
    }


def list_unread_changes(user_id):
    notifications = (
        UserBadgeNotification.query.filter_by(user_id=user_id, read_at=None)
        .order_by(UserBadgeNotification.created_at.asc(), UserBadgeNotification.id.asc())
        .all()
    )
    if not notifications:
        return {"total": 0, "list": []}

    definitions = _active_definitions({item.badge_code for item in notifications})
    definition_by_code = {item["code"]: item for item in definitions}
    return {
        "total": len(notifications),
        "list": [
            _format_badge_notification(item, definition_by_code.get(item.badge_code))
            for item in notifications
        ],
    }


def mark_changes_read(user_id, change_ids=None):
    query = UserBadgeNotification.query.filter_by(user_id=user_id, read_at=None)
    if change_ids is not None:
        if not isinstance(change_ids, list):
            raise ValueError("changeIds 必须为数组")
        normalized_ids = []
        for item in change_ids:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("changeIds 必须包含非空字符串")
            normalized_ids.append(item.strip())
        if not normalized_ids:
            return {"updated": 0}
        query = query.filter(UserBadgeNotification.id.in_(normalized_ids))

    now = datetime.utcnow()
    rows = query.all()
    for row in rows:
        row.read_at = now
    db.session.commit()
    return {"updated": len(rows)}


def collect_metrics(user_id, metric_keys=None):
    metric_keys = set(metric_keys or [])
    values = defaultdict(int)
    if "fortune_exists" in metric_keys:
        values["fortune_exists"] = 1 if FortuneRecord.query.filter_by(user_id=user_id).first() else 0
    if "diary_days" in metric_keys:
        values["diary_days"] = _count_distinct(DiaryEntry, "created_date", user_id)
    if "answer_count" in metric_keys:
        values["answer_count"] = AnswerRecord.query.filter_by(user_id=user_id).count()
    if "lucky_fortune_streak" in metric_keys:
        values["lucky_fortune_streak"] = _current_lucky_fortune_streak(user_id)
    if "login_streak" in metric_keys:
        values["login_streak"] = _current_login_streak(user_id)
    if "plaza_card_count" in metric_keys:
        values["plaza_card_count"] = PlazaCard.query.filter_by(user_id=user_id).count()
    if "favorite_count" in metric_keys:
        values["favorite_count"] = Favorite.query.filter_by(user_id=user_id).count()
    if "plaza_interaction_count" in metric_keys:
        like_count = Like.query.filter_by(user_id=user_id).count()
        comment_count = PlazaComment.query.filter(
            PlazaComment.user_id == user_id,
            PlazaComment.status != "deleted",
        ).count()
        values["plaza_interaction_count"] = like_count + comment_count
    if "fortune_days" in metric_keys:
        values["fortune_days"] = _count_distinct(FortuneRecord, "date", user_id)
    return values


def _count_distinct(model_cls, column_name, user_id):
    column = getattr(model_cls, column_name)
    return db.session.query(db.func.count(db.distinct(column))).filter(model_cls.user_id == user_id).scalar() or 0


def _current_login_streak(user_id):
    dates = [
        row.login_date
        for row in UserLoginDay.query.filter_by(user_id=user_id).order_by(UserLoginDay.login_date.desc()).all()
    ]
    return _max_streak_from_dates(dates)


def _current_lucky_fortune_streak(user_id):
    rows = (
        FortuneRecord.query.filter(FortuneRecord.user_id == user_id, FortuneRecord.score >= LUCKY_SCORE_THRESHOLD)
        .order_by(FortuneRecord.date.desc())
        .all()
    )
    dates = [row.date for row in rows]
    return _max_streak_from_dates(dates)


def _current_streak_from_dates(dates, start_date=None):
    unique_dates = sorted({item for item in dates if item}, reverse=True)
    if not unique_dates:
        return 0
    expected = start_date or unique_dates[0]
    if unique_dates[0] != expected:
        return 0
    count = 0
    for value in unique_dates:
        if value != expected:
            break
        count += 1
        expected = expected - timedelta(days=1)
    return count


def _max_streak_from_dates(dates):
    unique_dates = sorted({item for item in dates if item})
    if not unique_dates:
        return 0

    best = 1
    current = 1
    previous = unique_dates[0]
    for value in unique_dates[1:]:
        if value == previous + timedelta(days=1):
            current += 1
        else:
            best = max(best, current)
            current = 1
        previous = value
    return max(best, current)


def _evaluate_definition(definition, metrics):
    levels = sorted(definition["levels"], key=lambda item: item["level"])
    metric_key = levels[0]["metric_key"]
    progress = int(metrics.get(metric_key, 0) or 0)
    achieved = [level for level in levels if progress >= int(level["threshold"])]
    achieved_level = achieved[-1]["level"] if achieved else 0
    next_level = next((level for level in levels if level["level"] > achieved_level), None)
    target_level = next_level or levels[-1]
    return {"level": achieved_level, "progress": progress, "target": int(target_level["threshold"])}


def _target_for_retained_level(definition, retained_level):
    levels = sorted(definition["levels"], key=lambda item: item["level"])
    next_level = next((level for level in levels if level["level"] > retained_level), None)
    target_level = next_level or levels[-1]
    return int(target_level["threshold"])


def _upsert_user_badge(user_id, definition, result, existing=None):
    now = datetime.utcnow()
    if existing:
        retained_level = max(existing.level, result["level"])
        existing.current_progress = result["progress"]
        existing.target = _target_for_retained_level(definition, retained_level)
        existing.last_evaluated_at = now
        if result["level"] > existing.level:
            existing.level = result["level"]
            if not existing.unlocked_at:
                existing.unlocked_at = now
        return existing

    row = UserBadge(
        user_id=user_id,
        badge_code=definition["code"],
        level=result["level"],
        current_progress=result["progress"],
        target=result["target"],
        unlocked_at=now if result["level"] > 0 else None,
        last_evaluated_at=now,
    )
    db.session.add(row)
    try:
        db.session.flush()
    except IntegrityError:
        _safe_rollback()
        row = UserBadge.query.filter_by(user_id=user_id, badge_code=definition["code"]).first()
        if not row:
            raise
        return _upsert_user_badge(user_id, definition, result, existing=row)
    return row


def _create_badge_notification(user_id, badge_code, level, change_type):
    db.session.add(
        UserBadgeNotification(
            user_id=user_id,
            badge_code=badge_code,
            level=level,
            change_type=change_type,
        )
    )


def _public_definition_payload(definition):
    return {
        "code": definition["code"],
        "name": definition["name"],
        "category": definition["category"],
        "description": definition["description"],
        "iconUrl": definition["icon_url"],
        "grayIconUrl": definition["gray_icon_url"],
        "sortOrder": definition["sort_order"],
        "levels": [
            {
                "level": level["level"],
                "title": level["title"],
                "conditionType": level["condition_type"],
                "metricKey": level["metric_key"],
                "threshold": level["threshold"],
                "description": level["description"],
            }
            for level in definition["levels"]
        ],
    }


def _format_badge_notification(notification, definition=None):
    level_payload = None
    if definition:
        level_payload = next(
            (item for item in definition["levels"] if item["level"] == notification.level),
            None,
        )
    return {
        "id": notification.id,
        "badgeCode": notification.badge_code,
        "badgeName": definition["name"] if definition else notification.badge_code,
        "category": definition["category"] if definition else None,
        "level": notification.level,
        "title": level_payload["title"] if level_payload else None,
        "changeType": notification.change_type,
        "iconUrl": definition["icon_url"] if definition else None,
        "grayIconUrl": definition["gray_icon_url"] if definition else None,
        "createdAt": notification.created_at.isoformat() + "Z" if notification.created_at else None,
    }


def _format_user_badge(definition, user_badge):
    level = user_badge.level if user_badge else 0
    levels = sorted(definition["levels"], key=lambda item: item["level"])
    current_level = next((item for item in levels if item["level"] == level), None)
    next_level = next((item for item in levels if item["level"] > level), None)
    max_level = levels[-1]["level"] if levels else 0
    progress = user_badge.current_progress if user_badge else 0
    target = user_badge.target if user_badge else (levels[0]["threshold"] if levels else 1)
    return {
        "code": definition["code"],
        "name": definition["name"],
        "category": definition["category"],
        "level": level,
        "maxLevel": max_level,
        "title": current_level["title"] if current_level else None,
        "nextTitle": next_level["title"] if next_level else None,
        "progress": progress,
        "target": target,
        "unlocked": level > 0,
        "unlockedAt": user_badge.unlocked_at.isoformat() + "Z" if user_badge and user_badge.unlocked_at else None,
        "iconUrl": definition["icon_url"],
        "grayIconUrl": definition["gray_icon_url"],
        "levels": [
            {"level": item["level"], "title": item["title"], "threshold": item["threshold"], "description": item["description"]}
            for item in levels
        ],
    }

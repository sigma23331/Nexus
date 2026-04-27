from datetime import date, datetime

from extensions import db
from models.diary import DiaryEntry, MoodType


def _to_mood_enum(mood_tag):
    try:
        return MoodType(mood_tag)
    except ValueError as err:
        raise ValueError("moodTag 必须为 happy | calm | sad | angry | tired") from err


def _format_entry(entry):
    return {
        "id": entry.id,
        "moodTag": entry.mood_tag.value,
        "content": entry.content,
        "createdAt": entry.created_at.isoformat() + "Z" if entry.created_at else None,
    }


def create_entry(user_id, mood_tag, content, is_public=False):
    text = (content or "").strip()
    if not text:
        raise ValueError("content 必须为非空字符串")
    if len(text) > 2000:
        raise ValueError("content 长度不能超过2000")

    entry = DiaryEntry(
        user_id=user_id,
        mood_tag=_to_mood_enum(mood_tag),
        content=text,
        is_public=bool(is_public),
        created_date=date.today(),
    )
    db.session.add(entry)
    db.session.commit()
    db.session.refresh(entry)

    return {
        "id": entry.id,
        "createdAt": entry.created_at.isoformat() + "Z" if entry.created_at else None,
    }


def list_timeline(user_id, page, limit, year_month=None):
    query = DiaryEntry.query.filter_by(user_id=user_id)

    if year_month:
        month_start = datetime.strptime(year_month, "%Y-%m").date()
        if month_start.month == 12:
            month_end = date(month_start.year + 1, 1, 1)
        else:
            month_end = date(month_start.year, month_start.month + 1, 1)
        query = query.filter(DiaryEntry.created_date >= month_start, DiaryEntry.created_date < month_end)

    pagination = query.order_by(DiaryEntry.created_date.desc(), DiaryEntry.created_at.desc())\
        .paginate(page=page, per_page=limit, error_out=False)

    items = []
    for entry in pagination.items:
        snippet = entry.content if len(entry.content) <= 25 else entry.content[:25] + "..."
        items.append(
            {
                "id": entry.id,
                "date": entry.created_date.isoformat() if entry.created_date else None,
                "weekday": entry.created_date.strftime("%A") if entry.created_date else None,
                "moodTag": entry.mood_tag.value,
                "snippet": snippet,
            }
        )

    return {
        "totalDays": pagination.total,
        "page": page,
        "limit": limit,
        "list": items,
    }


def get_entry(user_id, entry_id):
    entry = DiaryEntry.query.filter_by(id=entry_id).first()
    if not entry:
        raise LookupError("日记不存在")
    if entry.user_id != user_id:
        raise PermissionError("无权访问他人日记")
    return _format_entry(entry)


def update_entry(user_id, entry_id, payload):
    entry = DiaryEntry.query.filter_by(id=entry_id).first()
    if not entry:
        raise LookupError("日记不存在")
    if entry.user_id != user_id:
        raise PermissionError("无权修改他人日记")

    has_change = False

    if "moodTag" in payload:
        entry.mood_tag = _to_mood_enum(payload.get("moodTag"))
        has_change = True

    if "content" in payload:
        text = (payload.get("content") or "").strip()
        if not text:
            raise ValueError("content 必须为非空字符串")
        if len(text) > 2000:
            raise ValueError("content 长度不能超过2000")
        entry.content = text
        has_change = True

    if "isPublic" in payload:
        entry.is_public = bool(payload.get("isPublic"))
        has_change = True

    if not has_change:
        raise ValueError("至少提供一个可更新字段")

    db.session.commit()
    db.session.refresh(entry)
    return _format_entry(entry)


def delete_entry(user_id, entry_id):
    entry = DiaryEntry.query.filter_by(id=entry_id).first()
    if not entry:
        raise LookupError("日记不存在")
    if entry.user_id != user_id:
        raise PermissionError("无权删除他人日记")

    db.session.delete(entry)
    db.session.commit()
    return {"success": True}

from datetime import date, timedelta

from models.fortune import FortuneRecord
from extensions import db
from services import content_generation_service


def _format_today_payload(record):
    return {
        "id": record.id,
        "date": record.date.isoformat(),
        "score": record.score,
        "title": record.title,
        "content": record.content,
        "yi": record.yi or [],
        "ji": record.ji or [],
        "luckyColor": record.lucky_color,
        "luckyDirection": record.lucky_direction,
    }


def get_today_fortune(user_id):
    today = date.today()
    record = FortuneRecord.query.filter_by(user_id=user_id, date=today).first()

    if not record:
        defaults = content_generation_service.generate_fortune(user_id=user_id, target_date=today)
        record = FortuneRecord(
            user_id=user_id,
            date=today,
            score=defaults["score"],
            title=defaults["title"],
            content=defaults["content"],
            yi=defaults["yi"],
            ji=defaults["ji"],
            lucky_color=defaults.get("luckyColor"),
            lucky_direction=defaults.get("luckyDirection"),
        )
        db.session.add(record)
        db.session.commit()
        db.session.refresh(record)

    return _format_today_payload(record)


def get_trend(user_id, days=7):
    end = date.today()
    start = end - timedelta(days=days - 1)

    records = FortuneRecord.query.filter(
        FortuneRecord.user_id == user_id,
        FortuneRecord.date >= start,
        FortuneRecord.date <= end,
    ).order_by(FortuneRecord.date.asc()).all()

    score_by_date = {record.date: record.score for record in records}
    points = []
    cursor = start
    while cursor <= end:
        points.append({
            "date": cursor.strftime("%m-%d"),
            "value": score_by_date.get(cursor, 0),
        })
        cursor += timedelta(days=1)

    return {"trendPoints": points}


def get_global_stats(target_date=None):
    target_date = target_date or date.today()
    records = FortuneRecord.query.filter_by(date=target_date).all()

    if not records:
        return {
            "date": target_date.isoformat(),
            "averageScore": 0,
            "topTitle": "",
            "topTitleRatio": 0,
            "totalParticipants": 0,
        }

    total_score = sum(record.score for record in records)
    average_score = round(total_score / len(records), 1)

    title_count = {}
    for record in records:
        title_count[record.title] = title_count.get(record.title, 0) + 1

    top_title = max(title_count, key=title_count.get)
    top_ratio = round(title_count[top_title] / len(records), 2)

    return {
        "date": target_date.isoformat(),
        "averageScore": average_score,
        "topTitle": top_title,
        "topTitleRatio": top_ratio,
        "totalParticipants": len(records),
    }

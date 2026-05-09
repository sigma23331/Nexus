import json
from datetime import date, timedelta

from models.fortune import FortuneRecord
from extensions import db
from services import content_generation_service


def _resolve_gua_meaning(score, delta=0):
    # 后端统一控制卦意文案，按“趋势 + 分数段”组合判断
    if delta >= 8:
        return ["雷火丰", "势能大开，宜果断推进"]
    if delta >= 3:
        if score >= 85:
            return ["火土相生", "顺势加速，宜主动求进"]
        return ["风雷益", "稳步加码，宜持续发力"]

    if delta <= -8:
        return ["坎水偏盛", "外扰较多，宜收敛守正"]
    if delta <= -3:
        if score >= 75:
            return ["山泽损", "减法增效，宜聚焦主线"]
        return ["水势偏重", "宜静守内观，先稳节奏"]

    if score >= 90:
        return ["乾元得势", "天行健，宜乘势突破"]
    if score >= 80:
        return ["木火通明", "思路清朗，宜扩展布局"]
    if score >= 70:
        return ["阴阳守中", "守正出新，宜稳步前行"]
    if score >= 60:
        return ["地山谦", "以退为进，宜夯实基础"]
    return ["坎离未济", "先养精蓄锐，再谋后动"]


def _resolve_lucky_hour(score):
    # 后端统一控制开运时辰文案，细化分档，避免前后端规则不一致
    if score >= 90:
        return {"name": "辰时", "range": "07:00-09:00"}
    if score >= 82:
        return {"name": "巳时", "range": "09:00-11:00"}
    if score >= 74:
        return {"name": "午时", "range": "11:00-13:00"}
    if score >= 66:
        return {"name": "未时", "range": "13:00-15:00"}
    return {"name": "酉时", "range": "17:00-19:00"}


def _serialize_content_pair(content_main, content_sub):
    main = str(content_main or "").strip()[:80]
    sub = str(content_sub or "").strip()[:80]
    return json.dumps([main, sub], ensure_ascii=False, separators=(",", ":"))


def _deserialize_content_pair(raw_content):
    fallback_sub = "稳中求进，心静则通达。"
    text = str(raw_content or "").strip()
    if not text:
        return "", fallback_sub

    try:
        parsed = json.loads(text)
        if isinstance(parsed, list) and len(parsed) >= 2:
            main = str(parsed[0] or "").strip()[:80]
            sub = str(parsed[1] or "").strip()[:80]
            return main, sub or fallback_sub
        if isinstance(parsed, dict):
            main = str(parsed.get("content_main", "") or "").strip()[:80]
            sub = str(parsed.get("content_sub", "") or "").strip()[:80]
            if main or sub:
                return main, sub or fallback_sub
    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    if "，" in text:
        first, rest = text.split("，", 1)
        return (first or text)[:80], (rest or fallback_sub)[:80]

    return text[:80], fallback_sub


def _format_today_payload(record, delta=0, record_existed=False):
    content_main, content_sub = _deserialize_content_pair(record.content)
    lucky_hour = _resolve_lucky_hour(record.score or 0)
    gua_lines = _resolve_gua_meaning(record.score or 0, delta)

    return {
        "id": record.id,
        "date": record.date.isoformat(),
        "score": record.score,
        "title": record.title,
        "content_main": content_main[:80],
        "content_sub": content_sub[:80],
        "love": "平稳",
        "career": "平稳",
        "health": "稳定",
        "wealth": "平稳",
        "yi": record.yi or [],
        "ji": record.ji or [],
        "gua_meaning_lines": gua_lines,
        "lucky_hour_name": lucky_hour["name"],
        "lucky_hour_range": lucky_hour["range"],
        "record_existed": bool(record_existed),
    }


def get_today_fortune(user_id):
    today = date.today()
    record = FortuneRecord.query.filter_by(user_id=user_id, date=today).first()
    record_existed = bool(record)

    if not record:
        defaults = content_generation_service.generate_fortune(user_id=user_id, target_date=today)
        record = FortuneRecord(
            user_id=user_id,
            date=today,
            score=defaults["score"],
            title=defaults["title"],
            content=_serialize_content_pair(defaults["content_main"], defaults["content_sub"]),
            yi=defaults["yi"],
            ji=defaults["ji"],
        )
        db.session.add(record)
        db.session.commit()
        db.session.refresh(record)

    previous_record = FortuneRecord.query.filter(
        FortuneRecord.user_id == user_id,
        FortuneRecord.date < today,
    ).order_by(FortuneRecord.date.desc()).first()
    previous_score = previous_record.score if previous_record else record.score
    delta = (record.score or 0) - (previous_score or 0)

    return _format_today_payload(record, delta=delta, record_existed=record_existed)


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

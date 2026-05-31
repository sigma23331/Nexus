import secrets
from datetime import date

from extensions import db
from models.fortune_pk import FortunePKRecord, FortunePKStatus
from models.user import User
from services import fortune_service


def _user_payload(user):
    if not user:
        return None
    return {
        "uid": user.id,
        "nickname": user.nickname,
        "avatar": user.avatar or "",
    }


def _format_pk(record):
    return {
        "id": record.id,
        "token": record.token,
        "status": record.status.value,
        "date": record.date.isoformat(),
        "challengerId": record.challenger_id,
        "challengerScore": record.challenger_score,
        "challenger": _user_payload(record.challenger),
        "defenderId": record.defender_id,
        "defenderScore": record.defender_score,
        "defender": _user_payload(record.defender),
        "result": record.result.value if record.result else None,
        "createdAt": record.created_at.isoformat() + "Z" if record.created_at else None,
        "completedAt": record.completed_at.isoformat() + "Z" if record.completed_at else None,
    }


def _generate_token():
    while True:
        token = secrets.token_urlsafe(24)[:32]
        if not FortunePKRecord.query.filter_by(token=token).first():
            return token


def _get_today_score(user_id):
    fortune = fortune_service.get_today_fortune(user_id=user_id)
    return int(fortune["score"])


def create_pk(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise LookupError("User not found")

    record = FortunePKRecord(
        token=_generate_token(),
        challenger_id=user_id,
        challenger_score=_get_today_score(user_id),
        date=date.today(),
        status=FortunePKStatus.PENDING,
    )
    db.session.add(record)
    db.session.commit()
    db.session.refresh(record)
    record.challenger = user

    return {
        "token": record.token,
        "pk": _format_pk(record),
    }


def get_or_join_pk(token, current_user_id=None):
    token = str(token or "").strip()
    if not token:
        raise ValueError("token is required")

    record = FortunePKRecord.query.filter_by(token=token).first()
    if not record:
        raise LookupError("PK not found")

    today = date.today()
    if record.status == FortunePKStatus.PENDING and record.date != today:
        record.status = FortunePKStatus.EXPIRED
        db.session.commit()
        raise PermissionError("PK link expired")

    if record.status == FortunePKStatus.EXPIRED:
        raise PermissionError("PK link expired")

    if record.status == FortunePKStatus.COMPLETED:
        return _format_pk(record)

    if not current_user_id:
        return _format_pk(record)

    if current_user_id == record.challenger_id:
        return _format_pk(record)

    defender = User.query.filter_by(id=current_user_id).first()
    if not defender:
        raise LookupError("User not found")

    locked_record = (
        FortunePKRecord.query.filter_by(token=token)
        .with_for_update()
        .first()
    )
    if not locked_record:
        raise LookupError("PK not found")
    if locked_record.status == FortunePKStatus.COMPLETED:
        return _format_pk(locked_record)
    if locked_record.status == FortunePKStatus.EXPIRED or locked_record.date != today:
        locked_record.status = FortunePKStatus.EXPIRED
        db.session.commit()
        raise PermissionError("PK link expired")
    if current_user_id == locked_record.challenger_id:
        return _format_pk(locked_record)

    locked_record.complete(defender_id=current_user_id, defender_score=_get_today_score(current_user_id))
    db.session.commit()
    db.session.refresh(locked_record)
    locked_record.defender = defender
    return _format_pk(locked_record)

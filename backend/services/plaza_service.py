import base64
from datetime import datetime

from extensions import db
from models.answer import AnswerRecord
from models.association import Like
from models.fortune import FortuneRecord
from models.plaza import CardType, PlazaCard
from models.user import User


def _encode_cursor(created_at, card_id):
    if not created_at:
        return None
    raw = f"{created_at.isoformat()}|{card_id}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("utf-8")


def _decode_cursor(cursor):
    if not cursor:
        return None, None
    try:
        raw = base64.urlsafe_b64decode(cursor.encode("utf-8")).decode("utf-8")
        created_at_text, card_id = raw.split("|", 1)
        return datetime.fromisoformat(created_at_text), card_id
    except Exception:
        raise ValueError("cursor 无效")


def _card_owner(user):
    return {
        "uid": user.id,
        "nickname": user.nickname,
        "avatar": user.avatar or "",
    }


def _format_card(card, current_user_id, liked_card_ids=None):
    if liked_card_ids is not None:
        is_liked = card.id in liked_card_ids
    else:
        is_liked = Like.query.filter_by(user_id=current_user_id, card_id=card.id).first() is not None
    return {
        "cardId": card.id,
        "type": card.type.value,
        "owner": _card_owner(card.user),
        "snapshotUrl": card.snapshot_url,
        "content": card.content,
        "stats": {
            "likes": card.likes_count,
            "isLiked": is_liked,
        },
        "createdAt": card.created_at.isoformat() + "Z" if card.created_at else None,
    }


def list_cards(user_id, tab="latest", cursor=None, limit=10):
    if tab not in ("hot", "latest"):
        raise ValueError("tab 必须为 hot | latest")
    if limit < 1 or limit > 20:
        raise ValueError("limit 范围 1-20")

    cursor_created_at, cursor_id = _decode_cursor(cursor)

    query = PlazaCard.query

    if tab == "hot":
        query = query.order_by(PlazaCard.likes_count.desc(), PlazaCard.created_at.desc(), PlazaCard.id.desc())
    else:
        query = query.order_by(PlazaCard.created_at.desc(), PlazaCard.id.desc())

    if cursor_created_at:
        query = query.filter(
            db.or_(
                PlazaCard.created_at < cursor_created_at,
                db.and_(PlazaCard.created_at == cursor_created_at, PlazaCard.id < cursor_id),
            )
        )

    rows = query.limit(limit + 1).all()
    has_more = len(rows) > limit
    current_rows = rows[:limit]
    next_cursor = None
    if has_more and current_rows:
        last = current_rows[-1]
        next_cursor = _encode_cursor(last.created_at, last.id)

    card_ids = [card.id for card in current_rows]
    liked_ids = {
        r.card_id for r in Like.query.filter(
            Like.user_id == user_id, Like.card_id.in_(card_ids)
        ).all()
    } if card_ids else set()

    return {
        "list": [_format_card(card, user_id, liked_ids) for card in current_rows],
        "nextCursor": next_cursor,
        "hasMore": has_more,
    }


def create_card(user_id, payload):
    card_type = payload.get("type")
    source_id = payload.get("sourceId")
    snapshot_url = payload.get("snapshotUrl")
    content = payload.get("content")
    tags = payload.get("tags")

    if card_type not in ("fortune", "answer"):
        raise ValueError("type 必须为 fortune | answer")
    if not isinstance(source_id, str) or not source_id.strip():
        raise ValueError("sourceId 字段不能为空")
    if not isinstance(snapshot_url, str) or not snapshot_url.startswith(("http://", "https://")):
        raise ValueError("snapshotUrl 必须为有效URL")
    if content is not None and (not isinstance(content, str) or len(content) > 100):
        raise ValueError("content 长度不能超过100")
    if tags is not None:
        if not isinstance(tags, list):
            raise ValueError("tags 必须为数组")
        if len(tags) > 3:
            raise ValueError("tags 最多3个")

    card = PlazaCard(
        user_id=user_id,
        type=CardType(card_type),
        snapshot_url=snapshot_url,
        content=content,
        tags=tags,
        likes_count=0,
    )

    if card_type == "answer":
        answer = AnswerRecord.query.filter_by(id=source_id.strip()).first()
        if not answer:
            raise LookupError("答案不存在")
        card.answer_id = answer.id
    else:
        fortune = FortuneRecord.query.filter_by(id=source_id.strip()).first()
        if not fortune:
            raise LookupError("运势不存在")
        card.fortune_id = fortune.id

    db.session.add(card)
    db.session.commit()
    db.session.refresh(card)

    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise LookupError("用户不存在")
    card.user = user

    return _format_card(card, user_id)


def toggle_like(user_id, card_id, action):
    if action not in ("like", "unlike"):
        raise ValueError("action 必须为 like | unlike")

    card = PlazaCard.query.filter_by(id=card_id).first()
    if not card:
        raise LookupError("card not found")

    relation = Like.query.filter_by(user_id=user_id, card_id=card_id).first()

    if action == "like":
        if not relation:
            db.session.add(Like(user_id=user_id, card_id=card_id))
            card.likes_count += 1
            db.session.commit()
        return {"cardId": card_id, "likes": card.likes_count, "isLiked": True}

    if relation:
        db.session.delete(relation)
        card.likes_count = max(0, card.likes_count - 1)
        db.session.commit()

    return {"cardId": card_id, "likes": card.likes_count, "isLiked": False}

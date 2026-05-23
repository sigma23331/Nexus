import base64
from datetime import datetime

from extensions import db
from models import PlazaCard, PlazaComment, PlazaCommentReport, User
from services import content_review_service


REPORT_HIDE_THRESHOLD = 2


def _encode_cursor(created_at, comment_id):
    if not created_at:
        return None
    raw = f"{created_at.isoformat()}|{comment_id}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("utf-8")


def _decode_cursor(cursor):
    if not cursor:
        return None, None
    try:
        raw = base64.urlsafe_b64decode(cursor.encode("utf-8")).decode("utf-8")
        created_at_text, comment_id = raw.split("|", 1)
        return datetime.fromisoformat(created_at_text), comment_id
    except Exception as exc:
        raise ValueError("cursor 无效") from exc


def _comment_owner(user):
    return {
        "uid": user.id,
        "nickname": user.nickname,
        "avatar": user.avatar or "",
    }


def _format_comment(comment, current_user_id, reply_preview=None, reply_count=None):
    reply_to_user = None
    if comment.reply_to_user:
        reply_to_user = _comment_owner(comment.reply_to_user)
    return {
        "commentId": comment.id,
        "cardId": comment.card_id,
        "owner": _comment_owner(comment.user),
        "content": comment.content,
        "parentId": comment.parent_id,
        "replyToUser": reply_to_user,
        "status": comment.status,
        "createdAt": comment.created_at.isoformat() + "Z" if comment.created_at else None,
        "canDelete": comment.user_id == current_user_id,
        "replyCount": reply_count if reply_count is not None else 0,
        "replies": reply_preview or [],
    }


def _visible_comment_query():
    return PlazaComment.query.filter_by(status="visible")


def _bump_comment_count(card_id, delta):
    if delta == 0:
        return
    card = PlazaCard.query.filter_by(id=card_id).first()
    if not card:
        raise LookupError("card not found")
    card.comments_count = max(0, int(card.comments_count or 0) + delta)


def list_comments(current_user_id, card_id, cursor=None, limit=20):
    if limit < 1 or limit > 20:
        raise ValueError("limit 范围 1-20")

    card = PlazaCard.query.filter_by(id=card_id).first()
    if not card:
        raise LookupError("card not found")

    cursor_created_at, cursor_id = _decode_cursor(cursor)
    query = _visible_comment_query().filter_by(card_id=card_id, parent_id=None).order_by(
        PlazaComment.created_at.desc(),
        PlazaComment.id.desc(),
    )
    if cursor_created_at:
        query = query.filter(
            db.or_(
                PlazaComment.created_at < cursor_created_at,
                db.and_(PlazaComment.created_at == cursor_created_at, PlazaComment.id < cursor_id),
            )
        )

    rows = query.limit(limit + 1).all()
    has_more = len(rows) > limit
    current_rows = rows[:limit]
    next_cursor = None
    if has_more and current_rows:
        last = current_rows[-1]
        next_cursor = _encode_cursor(last.created_at, last.id)

    top_ids = [item.id for item in current_rows]
    reply_counts = {}
    reply_preview_map = {item.id: [] for item in current_rows}
    if top_ids:
        replies = (
            _visible_comment_query()
            .filter(PlazaComment.parent_id.in_(top_ids))
            .order_by(PlazaComment.created_at.asc(), PlazaComment.id.asc())
            .all()
        )
        for reply in replies:
            reply_counts[reply.parent_id] = reply_counts.get(reply.parent_id, 0) + 1
            preview = reply_preview_map.setdefault(reply.parent_id, [])
            if len(preview) < 2:
                preview.append(_format_comment(reply, current_user_id, reply_preview=[], reply_count=0))

    return {
        "list": [
            _format_comment(
                comment,
                current_user_id,
                reply_preview=reply_preview_map.get(comment.id, []),
                reply_count=reply_counts.get(comment.id, 0),
            )
            for comment in current_rows
        ],
        "nextCursor": next_cursor,
        "hasMore": has_more,
    }


def list_replies(current_user_id, comment_id, cursor=None, limit=20):
    if limit < 1 or limit > 20:
        raise ValueError("limit 范围 1-20")

    parent = PlazaComment.query.filter_by(id=comment_id).first()
    if not parent:
        raise LookupError("comment not found")
    if parent.parent_id is not None:
        raise ValueError("只能查看顶级评论的回复")

    cursor_created_at, cursor_id = _decode_cursor(cursor)
    query = _visible_comment_query().filter_by(parent_id=comment_id).order_by(
        PlazaComment.created_at.asc(),
        PlazaComment.id.asc(),
    )
    if cursor_created_at:
        query = query.filter(
            db.or_(
                PlazaComment.created_at > cursor_created_at,
                db.and_(PlazaComment.created_at == cursor_created_at, PlazaComment.id > cursor_id),
            )
        )

    rows = query.limit(limit + 1).all()
    has_more = len(rows) > limit
    current_rows = rows[:limit]
    next_cursor = None
    if has_more and current_rows:
        last = current_rows[-1]
        next_cursor = _encode_cursor(last.created_at, last.id)

    return {
        "list": [_format_comment(comment, current_user_id, reply_preview=[], reply_count=0) for comment in current_rows],
        "nextCursor": next_cursor,
        "hasMore": has_more,
    }


def create_comment(user_id, card_id, content, parent_id=None):
    card = PlazaCard.query.filter_by(id=card_id).first()
    if not card:
        raise LookupError("card not found")

    text = str(content or "").strip()
    if not text:
        raise ValueError("content 字段不能为空")
    if len(text) > 200:
        raise ValueError("content 长度不能超过200")

    parent = None
    reply_to_user_id = None
    if parent_id:
        parent = PlazaComment.query.filter_by(id=parent_id).first()
        if not parent:
            raise LookupError("parent comment not found")
        if parent.card_id != card_id:
            raise ValueError("parentId 与 cardId 不匹配")
        if parent.parent_id is not None:
            raise ValueError("仅支持一级回复")
        reply_to_user_id = parent.user_id

    review = content_review_service.review_user_generated_text(
        scene="plaza_comment_content",
        text=text,
        user_id=user_id,
        target_type="plaza_comment",
    )
    if review.action == content_review_service.ACTION_REJECT:
        raise ValueError("评论内容包含敏感或高风险信息，请调整后重试")

    status = "visible" if review.action == content_review_service.ACTION_PASS else "pending_review"
    comment = PlazaComment(
        card_id=card_id,
        user_id=user_id,
        parent_id=parent_id,
        reply_to_user_id=reply_to_user_id,
        content=text,
        status=status,
        moderation_status=review.action,
        moderation_source=review.provider_name,
        moderation_reason=review.reason_code,
        updated_at=datetime.utcnow(),
    )
    db.session.add(comment)
    if status == "visible":
        _bump_comment_count(card_id=card_id, delta=1)
    db.session.commit()
    db.session.refresh(comment)

    if not comment.user:
        comment.user = User.query.filter_by(id=user_id).first()
    if comment.reply_to_user_id and not comment.reply_to_user:
        comment.reply_to_user = User.query.filter_by(id=comment.reply_to_user_id).first()

    return _format_comment(comment, user_id, reply_preview=[], reply_count=0)


def delete_comment(user_id, comment_id):
    comment = PlazaComment.query.filter_by(id=comment_id).first()
    if not comment:
        raise LookupError("comment not found")
    if comment.user_id != user_id:
        raise PermissionError("无权删除他人评论")
    if comment.status == "deleted":
        return {"success": True}

    if comment.status == "visible":
        _bump_comment_count(card_id=comment.card_id, delta=-1)
    comment.status = "deleted"
    comment.deleted_at = datetime.utcnow()
    comment.updated_at = datetime.utcnow()
    db.session.commit()
    return {"success": True}


def report_comment(user_id, comment_id, reason_code, reason_text=None):
    comment = PlazaComment.query.filter_by(id=comment_id).first()
    if not comment:
        raise LookupError("comment not found")

    text = str(reason_text or "").strip()
    if text:
        if len(text) > 200:
            raise ValueError("reasonText 长度不能超过200")
        review = content_review_service.review_user_generated_text(
            scene="comment_report_reason",
            text=text,
            user_id=user_id,
            target_type="plaza_comment",
            target_id=comment_id,
        )
        if review.action != content_review_service.ACTION_PASS:
            raise ValueError("举报补充说明包含敏感或高风险信息，请调整后重试")

    exists = PlazaCommentReport.query.filter_by(reporter_user_id=user_id, comment_id=comment_id).first()
    if exists:
        raise ValueError("请勿重复举报")

    report = PlazaCommentReport(
        comment_id=comment_id,
        reporter_user_id=user_id,
        reason_code=reason_code,
        reason_text=text or None,
        status="open",
    )
    db.session.add(report)
    db.session.flush()

    report_count = PlazaCommentReport.query.filter_by(comment_id=comment_id).count()
    if report_count >= REPORT_HIDE_THRESHOLD and comment.status == "visible":
        comment.status = "hidden"
        comment.moderation_status = "review"
        comment.moderation_source = "report"
        comment.moderation_reason = "REPORT_THRESHOLD_REACHED"
        comment.updated_at = datetime.utcnow()
        _bump_comment_count(card_id=comment.card_id, delta=-1)

    db.session.commit()
    return {"success": True, "reportCount": report_count}

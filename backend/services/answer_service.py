from models.answer import AnswerRecord
from models.association import Favorite
from extensions import db
from services import content_generation_service
from services import content_review_service


SAFE_FALLBACK_ANSWER = "先把心放稳一点，答案会慢慢清晰。"


def _fallback_review_result(reason_code="AI_OUTPUT_REVIEW_UNAVAILABLE"):
    return content_review_service.ReviewResult(
        action=content_review_service.ACTION_FALLBACK,
        labels=["review_error"],
        reason_code=reason_code,
        severity=content_review_service.SEVERITY_MEDIUM,
    )


def _review_question_or_raise(user_id, question):
    result = content_review_service.review_user_generated_text(
        scene="answer_question_input",
        text=question,
        user_id=user_id,
        target_type="answer_question",
    )
    if result.action != content_review_service.ACTION_PASS:
        raise ValueError("问题内容包含敏感或高风险信息，请调整后重试")


def _review_ai_answer(text, user_id):
    try:
        return content_review_service.review_ai_generated_text(
            scene="answer_output",
            text=text,
            user_id=user_id,
            target_type="answer_output",
        )
    except Exception:
        return _fallback_review_result()


def _generate_safe_answer(question, user_id):
    generation = content_generation_service.generate_answer(question=question, user_id=user_id)
    answer_text = generation["answerText"]
    review = _review_ai_answer(answer_text, user_id)
    if review.action == content_review_service.ACTION_PASS:
        return answer_text

    regenerated = content_generation_service.generate_answer(question=question, user_id=user_id)
    regenerated_text = regenerated["answerText"]
    second_review = _review_ai_answer(regenerated_text, user_id)
    if second_review.action == content_review_service.ACTION_PASS:
        return regenerated_text

    return SAFE_FALLBACK_ANSWER


def ask_question(user_id, question):
    normalized_question = question.strip()
    _review_question_or_raise(user_id=user_id, question=normalized_question)
    answer_text = _generate_safe_answer(question=normalized_question, user_id=user_id)

    record = AnswerRecord(
        user_id=user_id,
        question=normalized_question,
        answer_text=answer_text,
    )
    db.session.add(record)
    db.session.commit()
    db.session.refresh(record)

    return {
        "id": record.id,
        "question": record.question,
        "answerText": record.answer_text,
        "createdAt": record.created_at.isoformat() + "Z" if record.created_at else None,
    }


def list_history(user_id, page, limit):
    pagination = AnswerRecord.query.filter_by(user_id=user_id)\
        .order_by(AnswerRecord.created_at.desc())\
        .paginate(page=page, per_page=limit, error_out=False)

    answer_ids = [record.id for record in pagination.items]
    favorited_ids = {
        r.answer_id for r in Favorite.query.filter(
            Favorite.user_id == user_id, Favorite.answer_id.in_(answer_ids)
        ).all()
    } if answer_ids else set()

    payload = []
    for record in pagination.items:
        payload.append({
            "id": record.id,
            "question": record.question,
            "answerText": record.answer_text,
            "createdAt": record.created_at.isoformat() + "Z" if record.created_at else None,
            "isFavorited": record.id in favorited_ids,
        })

    return {
        "total": pagination.total,
        "page": page,
        "limit": limit,
        "list": payload,
    }


def toggle_favorite(user_id, answer_id, action):
    answer = AnswerRecord.query.filter_by(id=answer_id).first()
    if not answer:
        raise LookupError("答案不存在")

    favorite = Favorite.query.filter_by(user_id=user_id, answer_id=answer_id).first()

    if action == "favorite":
        if not favorite:
            db.session.add(Favorite(user_id=user_id, answer_id=answer_id))
            db.session.commit()
        return {"answerId": answer_id, "isFavorited": True}

    if favorite:
        db.session.delete(favorite)
        db.session.commit()

    return {"answerId": answer_id, "isFavorited": False}

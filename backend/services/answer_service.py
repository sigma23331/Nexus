from models.answer import AnswerRecord
from models.association import Favorite
from extensions import db
from services import content_generation_service


def ask_question(user_id, question):
    generation = content_generation_service.generate_answer(question=question, user_id=user_id)

    record = AnswerRecord(
        user_id=user_id,
        question=question.strip(),
        answer_text=generation["answerText"],
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

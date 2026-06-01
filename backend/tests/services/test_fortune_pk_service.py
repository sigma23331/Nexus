from datetime import date, datetime
from types import SimpleNamespace

import pytest

from models.fortune_pk import FortunePKRecord, FortunePKResult, FortunePKStatus
from services import fortune_pk_service


def test_complete_sets_result_and_timestamp_for_defender_win():
    record = FortunePKRecord(
        challenger_id="u1",
        challenger_score=60,
        date=date.today(),
    )

    record.complete(defender_id="u2", defender_score=88)

    assert record.defender_id == "u2"
    assert record.defender_score == 88
    assert record.result == FortunePKResult.DEFENDER_WIN
    assert record.status == FortunePKStatus.COMPLETED
    assert record.completed_at is not None


def test_complete_rejects_self_pk():
    record = FortunePKRecord(
        challenger_id="u1",
        challenger_score=60,
        date=date.today(),
    )

    with pytest.raises(ValueError):
        record.complete(defender_id="u1", defender_score=88)


def test_format_pk_serializes_result_and_users():
    record = SimpleNamespace(
        id="pk1",
        token="token-1",
        status=FortunePKStatus.COMPLETED,
        date=date(2026, 5, 31),
        challenger_id="u1",
        challenger_score=90,
        challenger=SimpleNamespace(id="u1", nickname="Alice", avatar=""),
        defender_id="u2",
        defender_score=90,
        defender=SimpleNamespace(id="u2", nickname="Bob", avatar="avatar.png"),
        result=FortunePKResult.DRAW,
        created_at=datetime(2026, 5, 31, 6, 0, 0),
        completed_at=datetime(2026, 5, 31, 6, 5, 0),
    )

    payload = fortune_pk_service._format_pk(record)

    assert payload["status"] == "completed"
    assert payload["result"] == "draw"
    assert payload["challenger"]["nickname"] == "Alice"
    assert payload["defender"]["avatar"] == "avatar.png"

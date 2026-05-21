from types import SimpleNamespace

from services import fortune_service


def test_deserialize_content_pair_with_json_array():
    raw = '["风起，云开","稳中求进，心静则明"]'

    main, sub = fortune_service._deserialize_content_pair(raw)

    assert main == "风起，云开"
    assert sub == "稳中求进，心静则明"


def test_deserialize_content_pair_with_legacy_text():
    raw = "风起云开，顺势自来"

    main, sub = fortune_service._deserialize_content_pair(raw)

    assert main == "风起云开"
    assert sub == "顺势自来"


def test_format_today_payload_reads_structured_content_and_dynamic_fields():
    record = SimpleNamespace(
        id="f1",
        date=SimpleNamespace(isoformat=lambda: "2026-04-28"),
        score=88,
        title="上上签",
        content='["风起，云开","稳中求进，心静则明"]',
        love="中上",
        career="平稳",
        health="稳定",
        wealth="向好",
        yi=["学习"],
        ji=["熬夜"],
        gua_meaning_lines=["火土相生", "顺势加速，主动求进"],
        lucky_hour_name="巳时",
        lucky_hour_range="09:00-11:00",
    )

    payload = fortune_service._format_today_payload(record)

    assert payload["content_main"] == "风起，云开"
    assert payload["content_sub"] == "稳中求进，心静则明"
    assert payload["love"] == "中上"
    assert payload["gua_meaning_lines"] == ["火土相生", "顺势加速，主动求进"]
    assert payload["lucky_hour_name"] == "巳时"

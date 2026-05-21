from tools.prompt_lab.selector import AnswerStyleSelector, FortuneContentSelector


def test_answer_selector_loads_and_selects(tmp_path):
    styles_dir = tmp_path / "answer" / "styles"
    styles_dir.mkdir(parents=True)
    (styles_dir / "poetic.txt").write_text("诗意型\n描述\n示例1\n示例2", encoding="utf-8")
    (styles_dir / "action.txt").write_text("行动型\n描述\n示例3\n示例4", encoding="utf-8")

    selector = AnswerStyleSelector(str(styles_dir))
    result = selector.select()

    assert isinstance(result, str)
    assert len(result) > 0


def test_answer_selector_selects_differently_across_calls(tmp_path):
    styles_dir = tmp_path / "styles"
    styles_dir.mkdir(parents=True)
    for name in ["a", "b", "c", "d", "e"]:
        (styles_dir / f"{name}.txt").write_text(f"{name}\ndesc\nex1\nex2", encoding="utf-8")

    selector = AnswerStyleSelector(str(styles_dir))
    results = {selector.select() for _ in range(20)}

    assert len(results) >= 2


def test_answer_selector_raises_on_empty_dir(tmp_path):
    styles_dir = tmp_path / "empty"
    styles_dir.mkdir(parents=True)

    import pytest

    with pytest.raises(ValueError, match="no style files found"):
        AnswerStyleSelector(str(styles_dir))


def _build_fortune_dirs(base):
    (base / "titles").mkdir(parents=True)
    (base / "titles" / "0-39.txt").write_text("tA||sA\ntB||sB", encoding="utf-8")
    (base / "titles" / "40-59.txt").write_text("tC||sC", encoding="utf-8")
    (base / "titles" / "60-74.txt").write_text("tD||sD", encoding="utf-8")
    (base / "titles" / "75-89.txt").write_text("tE||sE", encoding="utf-8")
    (base / "titles" / "90-100.txt").write_text("tF||sF", encoding="utf-8")
    (base / "keywords").mkdir(parents=True)
    (base / "keywords" / "love.txt").write_text("平稳\n桃花\n宜静", encoding="utf-8")
    (base / "keywords" / "career.txt").write_text("向好\n需沟通\n稳扎稳打", encoding="utf-8")
    (base / "keywords" / "health.txt").write_text("稳定\n需注意\n活力恢复", encoding="utf-8")
    (base / "keywords" / "wealth.txt").write_text("平稳\n谨慎\n有惊喜", encoding="utf-8")
    (base / "yiji").mkdir(parents=True)
    (base / "yiji" / "yi.txt").write_text("早睡\n学习\n散步", encoding="utf-8")
    (base / "yiji" / "ji.txt").write_text("熬夜\n冲动\n争执", encoding="utf-8")


def test_fortune_selector_title_matches_score(tmp_path):
    base = tmp_path / "fortune"
    _build_fortune_dirs(base)
    selector = FortuneContentSelector(str(base))

    result = selector.select_title(55)
    assert result["main"] in ("tC",)
    assert result["sub"] in ("sC",)

    result2 = selector.select_title(30)
    assert result2["main"] in ("tA", "tB")


def test_fortune_selector_keywords_return_all_categories(tmp_path):
    base = tmp_path / "fortune"
    _build_fortune_dirs(base)
    selector = FortuneContentSelector(str(base))

    kw = selector.select_keywords({"topic_interests": ["career"]})
    assert set(kw.keys()) == {"love", "career", "health", "wealth"}
    assert kw["career"] in ("向好", "需沟通", "稳扎稳打")


def test_fortune_selector_keywords_fallback_on_empty_profile(tmp_path):
    base = tmp_path / "fortune"
    _build_fortune_dirs(base)
    selector = FortuneContentSelector(str(base))

    kw = selector.select_keywords(None)
    assert set(kw.keys()) == {"love", "career", "health", "wealth"}


def test_fortune_selector_yiji_returns_dict(tmp_path):
    base = tmp_path / "fortune"
    _build_fortune_dirs(base)
    selector = FortuneContentSelector(str(base))

    result = selector.select_yiji({"topic_interests": []})
    assert "yi" in result
    assert "ji" in result
    assert len(result["yi"]) > 0
    assert len(result["ji"]) > 0


def test_fortune_selector_keywords_are_stable_for_same_profile(tmp_path, monkeypatch):
    base = tmp_path / "fortune"
    _build_fortune_dirs(base)
    selector = FortuneContentSelector(str(base))

    monkeypatch.setattr("tools.prompt_lab.selector.random.random", lambda: 0.8)

    profile = {
        "topic_interests": ["job_seek", "goal_job_change"],
        "mood_tendency": "optimistic|high_friction|mid_energy",
        "self_context_tag": "graduation|job_seek|sleep_low",
    }
    first = selector.select_keywords(profile)
    second = selector.select_keywords(profile)

    assert first == second


def test_fortune_selector_keywords_ranked_prefers_profile_tokens(tmp_path, monkeypatch):
    base = tmp_path / "fortune"
    _build_fortune_dirs(base)
    (base / "keywords" / "career.txt").write_text("平稳推进\njob_seek冲刺\n沟通协作", encoding="utf-8")
    selector = FortuneContentSelector(str(base))

    monkeypatch.setattr("tools.prompt_lab.selector.random.random", lambda: 0.8)

    selected, debug_meta = selector.select_keywords_ranked(
        {
            "topic_interests": ["job_seek"],
            "mood_tendency": "steady",
            "self_context_tag": "campus",
        },
        context=None,
        k=3,
        explore_rate=0.1,
    )

    assert selected["career"] == "job_seek冲刺"
    assert debug_meta["strategy"] == "exploit"


def test_fortune_selector_keywords_ranked_is_backward_compatible_shape(tmp_path, monkeypatch):
    base = tmp_path / "fortune"
    _build_fortune_dirs(base)
    selector = FortuneContentSelector(str(base))

    monkeypatch.setattr("tools.prompt_lab.selector.random.random", lambda: 0.8)

    selected, debug_meta = selector.select_keywords_ranked(None, context=None)

    assert set(selected.keys()) == {"love", "career", "health", "wealth"}
    assert "candidates" in debug_meta


def test_fortune_selector_keywords_uses_default_explore_rate(tmp_path, monkeypatch):
    base = tmp_path / "fortune"
    _build_fortune_dirs(base)
    (base / "keywords" / "career.txt").write_text("job_seek核心\n普通方案A\n普通方案B", encoding="utf-8")
    selector = FortuneContentSelector(str(base))

    monkeypatch.setattr("tools.prompt_lab.selector.random.random", lambda: 0.0)
    monkeypatch.setattr("tools.prompt_lab.selector.random.choice", lambda seq: seq[0])

    selected = selector.select_keywords(
        {
            "topic_interests": ["job_seek"],
            "mood_tendency": "steady",
            "self_context_tag": "campus",
        }
    )

    assert selected["career"] != "job_seek核心"


def test_fortune_selector_keywords_ranked_diversifies_by_context_key(tmp_path):
    base = tmp_path / "fortune"
    _build_fortune_dirs(base)
    (base / "keywords" / "career.txt").write_text("方案甲\n方案乙\n方案丙\n方案丁", encoding="utf-8")
    selector = FortuneContentSelector(str(base), default_explore_rate=0.0)

    profile = {
        "topic_interests": ["unknown_topic"],
        "mood_tendency": "neutral",
        "self_context_tag": "daily",
    }

    first, _ = selector.select_keywords_ranked(
        profile,
        context={"diversify_key": "user-a-2026-05-04"},
        k=4,
        explore_rate=0.0,
    )
    second, _ = selector.select_keywords_ranked(
        profile,
        context={"diversify_key": "user-b-2026-05-04"},
        k=4,
        explore_rate=0.0,
    )

    assert first["career"] != second["career"]


def test_fortune_selector_yiji_ranked_avoids_same_action_prefix(tmp_path):
    base = tmp_path / "fortune"
    _build_fortune_dirs(base)
    (base / "yiji" / "yi.txt").write_text("整理书桌\n整理房间\n散步十分钟\n复盘计划", encoding="utf-8")
    selector = FortuneContentSelector(str(base), default_explore_rate=0.0)

    selected, _ = selector.select_yiji_ranked(
        profile={"topic_interests": [], "mood_tendency": "", "self_context_tag": ""},
        context={"diversify_key": "user-a-2026-05-04"},
        k=4,
        per_bucket=2,
        explore_rate=0.0,
    )

    assert len(selected["yi"]) == 2
    assert not (selected["yi"][0].startswith("整理") and selected["yi"][1].startswith("整理"))


def test_fortune_selector_yiji_ranked_penalizes_recent_shown_ids(tmp_path):
    base = tmp_path / "fortune"
    _build_fortune_dirs(base)
    (base / "yiji" / "yi.txt").write_text("整理书桌\n散步十分钟\n复盘计划", encoding="utf-8")
    selector = FortuneContentSelector(str(base), default_explore_rate=0.0)

    selected, _ = selector.select_yiji_ranked(
        profile={"topic_interests": [], "mood_tendency": "", "self_context_tag": ""},
        context={"recent_shown_ids": ["yi:整理书桌", "yi:整理书桌", "yi:整理书桌"]},
        k=3,
        per_bucket=1,
        explore_rate=0.0,
    )

    assert selected["yi"][0] != "整理书桌"


def test_fortune_selector_yiji_ranked_diversifies_by_context_key(tmp_path):
    base = tmp_path / "fortune"
    _build_fortune_dirs(base)
    (base / "yiji" / "yi.txt").write_text("整理书桌\n散步十分钟\n复盘计划\n喝水", encoding="utf-8")
    selector = FortuneContentSelector(str(base), default_explore_rate=0.0)

    first, _ = selector.select_yiji_ranked(
        profile={"topic_interests": [], "mood_tendency": "", "self_context_tag": ""},
        context={"diversify_key": "user-a-2026-05-04"},
        k=4,
        per_bucket=1,
        explore_rate=0.0,
    )
    second, _ = selector.select_yiji_ranked(
        profile={"topic_interests": [], "mood_tendency": "", "self_context_tag": ""},
        context={"diversify_key": "user-b-2026-05-04"},
        k=4,
        per_bucket=1,
        explore_rate=0.0,
    )

    assert first["yi"] != second["yi"]

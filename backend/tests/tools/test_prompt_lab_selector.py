from tools.prompt_lab.selector import AnswerStyleSelector, FortuneContentSelector, stable_fortune_score


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


def test_stable_fortune_score_is_stable_for_same_user_and_date():
    context = {
        "virtual_user_id": "u1",
        "birthday": "2001-02-03",
    }

    first = stable_fortune_score(context, "2026-04-25")
    second = stable_fortune_score(context, "2026-04-25")

    assert first == second
    assert 0 <= first <= 100


def test_stable_fortune_score_changes_with_date():
    context = {
        "virtual_user_id": "u1",
        "birthday": "2001-02-03",
    }

    assert stable_fortune_score(context, "2026-04-25") != stable_fortune_score(context, "2026-04-26")


def test_fortune_selector_keywords_use_random_choice(tmp_path, monkeypatch):
    base = tmp_path / "fortune"
    _build_fortune_dirs(base)
    selector = FortuneContentSelector(str(base))

    monkeypatch.setattr("tools.prompt_lab.selector.random.choice", lambda seq: seq[-1])

    selected = selector.select_keywords({"topic_interests": ["career"]})

    assert selected["career"] == "稳扎稳打"

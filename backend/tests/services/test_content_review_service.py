from services import content_review_service


def test_is_content_safe_returns_true_for_clean_text():
    passed, processed = content_review_service.is_content_safe("今天状态不错，继续加油")

    assert passed is True
    assert processed == "今天状态不错，继续加油"


def test_is_content_safe_masks_blocked_patterns_case_insensitive():
    passed, processed = content_review_service.is_content_safe("你这人真傻逼，别骂妈的")

    assert passed is False
    assert "傻逼" not in processed
    assert "妈的" not in processed
    assert processed.count("***") >= 2

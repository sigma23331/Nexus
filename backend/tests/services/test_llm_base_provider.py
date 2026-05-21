import pytest

from services.llm.providers.base import LLMProvider


def test_base_provider_methods_raise_not_implemented():
    with pytest.raises(NotImplementedError):
        LLMProvider.generate_answer(object(), "q", "u1")

    with pytest.raises(NotImplementedError):
        LLMProvider.generate_fortune(object(), "u1", None)

    with pytest.raises(NotImplementedError):
        LLMProvider.analyze_user_profile(object(), [], [])

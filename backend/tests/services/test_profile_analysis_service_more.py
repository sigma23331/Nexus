from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from services.profile_analysis_service import ProfileAnalysisService


class _Field:
    def __eq__(self, _other):
        return True

    def __le__(self, _other):
        return True

    @staticmethod
    def asc():
        return None


def test_enqueue_analysis_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        ProfileAnalysisService.enqueue_analysis("", "evt", datetime.utcnow())

    with pytest.raises(ValueError):
        ProfileAnalysisService.enqueue_analysis("u1", "", datetime.utcnow())

    with pytest.raises(ValueError):
        ProfileAnalysisService.enqueue_analysis("u1", "evt", "bad")


def test_need_analysis_respects_profile_updated_at(monkeypatch):
    class _Query:
        def __init__(self, profile):
            self.profile = profile

        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return self.profile

    class _UserProfile:
        query = _Query(SimpleNamespace(updated_at=datetime.utcnow() - timedelta(minutes=10)))

    monkeypatch.setattr("services.profile_analysis_service.UserProfile", _UserProfile)
    assert ProfileAnalysisService._need_analysis("u1") is False

    _UserProfile.query = _Query(SimpleNamespace(updated_at=datetime.utcnow() - timedelta(hours=25)))
    assert ProfileAnalysisService._need_analysis("u1") is True


def test_apply_ai_analysis_result_creates_profile_and_normalizes_fields(monkeypatch):
    added = []
    flushed = []

    class _Session:
        def add(self, value):
            added.append(value)

        def flush(self):
            flushed.append(True)

    monkeypatch.setattr("services.profile_analysis_service.db.session", _Session())

    class _Query:
        def filter_by(self, **_kwargs):
            return self

        def first(self):
            return None

    class _UserProfile:
        query = _Query()

        def __init__(self, user_id, topic_interests, personalization_enabled):
            self.user_id = user_id
            self.topic_interests = topic_interests
            self.personalization_enabled = personalization_enabled
            self.mood_tendency = None
            self.self_context_tag = None

    monkeypatch.setattr("services.profile_analysis_service.UserProfile", _UserProfile)

    profile = ProfileAnalysisService.apply_ai_analysis_result(
        "u1",
        {"mood_tendency": "calm", "topic_interests": "bad", "self_context_tag": "x" * 30},
    )

    assert profile.user_id == "u1"
    assert profile.topic_interests == []
    assert len(profile.self_context_tag) == 20
    assert added and flushed


def test_process_one_job_handles_success_and_failure(monkeypatch):
    commits = []

    class _Session:
        def flush(self):
            return None

        def commit(self):
            commits.append(True)

    monkeypatch.setattr("services.profile_analysis_service.db.session", _Session())

    success_job = SimpleNamespace(
        user_id="u1",
        window_days=7,
        status="pending",
        started_at=None,
        attempt_count=0,
        max_attempts=3,
        result_text=None,
        finished_at=None,
        error_message=None,
        next_run_at=None,
    )

    monkeypatch.setattr(ProfileAnalysisService, "pick_next_job", staticmethod(lambda now=None: success_job))
    monkeypatch.setattr(ProfileAnalysisService, "analyze_profile_with_llm", staticmethod(lambda **_: {"mood_tendency": "calm"}))
    monkeypatch.setattr(ProfileAnalysisService, "apply_ai_analysis_result", staticmethod(lambda *_args, **_kwargs: None))

    out_success = ProfileAnalysisService.process_one_job()
    assert out_success.status == "succeeded"

    fail_job = SimpleNamespace(
        user_id="u2",
        window_days=7,
        status="pending",
        started_at=None,
        attempt_count=2,
        max_attempts=3,
        result_text=None,
        finished_at=None,
        error_message=None,
        next_run_at=None,
    )

    monkeypatch.setattr(ProfileAnalysisService, "pick_next_job", staticmethod(lambda now=None: fail_job))

    def _raise(**_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(ProfileAnalysisService, "analyze_profile_with_llm", staticmethod(_raise))

    out_fail = ProfileAnalysisService.process_one_job()
    assert out_fail.status == "failed_terminal"
    assert "boom" in out_fail.error_message
    assert commits


def test_trigger_analysis_if_needed_swallows_generation_failure(monkeypatch):
    calls = {"rollback": 0}

    class _Session:
        def rollback(self):
            calls["rollback"] += 1

    monkeypatch.setattr("services.profile_analysis_service.db.session", _Session())
    monkeypatch.setattr(ProfileAnalysisService, "_need_analysis", staticmethod(lambda _user_id: True))

    def _raise(*_args, **_kwargs):
        raise RuntimeError("llm down")

    monkeypatch.setattr(ProfileAnalysisService, "analyze_profile_with_llm", staticmethod(_raise))

    assert ProfileAnalysisService.trigger_analysis_if_needed("u1") is None
    assert calls["rollback"] == 1

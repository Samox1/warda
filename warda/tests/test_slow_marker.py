"""A test marked `slow` is skipped unless WARDA_SLOW=1."""

import pytest


def test_slow_marked_test_is_skipped_without_warda_slow(
    pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("WARDA_SLOW", raising=False)
    pytester.makepyfile(
        """
        from warda.tests.conftest import slow


        @slow
        def test_runs_only_when_slow():
            assert True
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(skipped=1)

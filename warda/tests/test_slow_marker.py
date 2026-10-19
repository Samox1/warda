"""A test marked `slow` runs only with WARDA_SLOW=1; the gate is the root `conftest.py` hook."""

from pathlib import Path

import pytest

ROOT_CONFTEST = Path(__file__).resolve().parents[2] / "conftest.py"


@pytest.mark.parametrize(("warda_slow", "outcomes"), [(None, {"skipped": 1}), ("1", {"passed": 1})])
def test_slow_marked_test_runs_only_with_warda_slow(
    pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch, warda_slow: str | None, outcomes: dict[str, int]
) -> None:
    if warda_slow is None:
        monkeypatch.delenv("WARDA_SLOW", raising=False)
    else:
        monkeypatch.setenv("WARDA_SLOW", warda_slow)
    pytester.makeconftest(ROOT_CONFTEST.read_text())
    pytester.makeini("[pytest]\nmarkers = slow\n")
    pytester.makepyfile(
        """
        import pytest


        @pytest.mark.slow
        def test_runs_only_when_slow():
            assert True
        """
    )
    pytester.runpytest().assert_outcomes(**outcomes)

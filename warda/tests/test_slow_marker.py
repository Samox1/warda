"""The root `conftest.py` collection gates: `slow` needs WARDA_SLOW=1, `requires_mlx` needs an importable `mlx`."""

import importlib.util
from pathlib import Path

import pytest

ROOT_CONFTEST = Path(__file__).resolve().parents[2] / "conftest.py"
MARKED_TEST = """
import pytest


@pytest.mark.{marker}
def test_gated():
    assert True
"""


def _gated_run(pytester: pytest.Pytester) -> pytest.RunResult:
    pytester.makeconftest(ROOT_CONFTEST.read_text())
    pytester.makeini("[pytest]\nmarkers =\n    slow\n    requires_mlx\n")
    return pytester.runpytest()


@pytest.mark.parametrize(("warda_slow", "outcomes"), [(None, {"skipped": 1}), ("1", {"passed": 1})])
def test_slow_marked_test_runs_only_with_warda_slow(
    pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch, warda_slow: str | None, outcomes: dict[str, int]
) -> None:
    if warda_slow is None:
        monkeypatch.delenv("WARDA_SLOW", raising=False)
    else:
        monkeypatch.setenv("WARDA_SLOW", warda_slow)
    pytester.makepyfile(MARKED_TEST.format(marker="slow"))
    _gated_run(pytester).assert_outcomes(**outcomes)


def test_unmarked_test_under_a_node_named_slow_still_runs(
    pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("WARDA_SLOW", raising=False)
    pytester.mkdir("slow")
    pytester.makepyfile(**{"slow/test_plain": "def test_plain():\n    assert True\n"})
    _gated_run(pytester).assert_outcomes(passed=1)


def test_requires_mlx_test_is_skipped_where_mlx_is_missing(
    pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_find_spec = importlib.util.find_spec
    monkeypatch.setattr(
        importlib.util, "find_spec", lambda name, *args: None if name == "mlx" else real_find_spec(name, *args)
    )
    pytester.makepyfile(MARKED_TEST.format(marker="requires_mlx"))
    _gated_run(pytester).assert_outcomes(skipped=1)

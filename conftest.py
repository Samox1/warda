"""Root pytest configuration: the pytester plugin and the capability / opt-in skips."""

from __future__ import annotations

import importlib.util
import os

import pytest

pytest_plugins = ["pytester"]


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Skip ``requires_mlx`` tests where MLX is not installed and ``slow`` tests unless ``WARDA_SLOW=1``.

    Both conditions are read here, at collection time, so the environment of the current session decides.
    """
    skips: list[tuple[str, pytest.MarkDecorator]] = []
    if importlib.util.find_spec("mlx") is None:
        skips.append(("requires_mlx", pytest.mark.skip(reason="mlx is not installed on this platform")))
    if os.environ.get("WARDA_SLOW") != "1":
        skips.append(("slow", pytest.mark.skip(reason="set WARDA_SLOW=1")))
    for item in items:
        for marker, skip in skips:
            if marker in item.keywords:
                item.add_marker(skip)

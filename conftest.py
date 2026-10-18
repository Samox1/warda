"""Root pytest configuration: the pytester plugin and the MLX capability skip."""

from __future__ import annotations

import importlib.util

import pytest

pytest_plugins = ["pytester"]


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Skip tests marked ``requires_mlx`` when MLX is not installed (non-Apple-Silicon platforms)."""
    if importlib.util.find_spec("mlx") is not None:
        return
    skip = pytest.mark.skip(reason="mlx is not installed on this platform")
    for item in items:
        if "requires_mlx" in item.keywords:
            item.add_marker(skip)

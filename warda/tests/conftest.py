"""Shared markers for `warda` tests."""

import os

import pytest

slow = pytest.mark.skipif(os.environ.get("WARDA_SLOW") != "1", reason="set WARDA_SLOW=1")

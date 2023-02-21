from __future__ import annotations

from .helpers import run


def test_version():
    actual = run(['version'])
    assert actual.count('.') == 2

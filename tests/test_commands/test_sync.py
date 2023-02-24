from __future__ import annotations

from io import StringIO
from pathlib import Path

from mypy_baseline import main

from .helpers import LINE1, LINE2


def test_sync(tmp_path: Path):
    blpath = tmp_path / 'bline.txt'
    stdin = StringIO()
    stdin.write(LINE1)
    stdin.write(LINE2)
    stdin.seek(0)
    code = main(['sync', '--baseline-path', str(blpath)], stdin, StringIO())
    assert code == 0
    actual = blpath.read_text()
    line1, line2 = actual.splitlines()
    assert line1 == 'views.py:0: error: Hello world  [assignment]'
    assert line2 == 'settings.py:0: error: How are you?  [union-attr]'

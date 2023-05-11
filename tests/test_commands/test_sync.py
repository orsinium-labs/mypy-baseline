from __future__ import annotations

from io import StringIO
from pathlib import Path

from mypy_baseline import main

from .helpers import LINE1, LINE2, LINE3, NOTEBOOK_LINE1


def test_sync(tmp_path: Path):
    blpath = tmp_path / 'bline.txt'
    stdin = StringIO()
    stdin.write(LINE1)
    stdin.write(LINE2)
    stdin.write(LINE3)
    stdin.seek(0)
    code = main(['sync', '--baseline-path', str(blpath)], stdin, StringIO())
    assert code == 0
    actual = blpath.read_text()
    line1, line2, line3 = actual.splitlines()
    assert line1 == 'views.py:0: error: Hello world  [assignment]'
    assert line2 == 'settings.py:0: error: How are you?  [union-attr]'
    assert line3 == 'python/utils.py:0: error: Second argument of Enum() must be string  [misc]'  # noqa: E501s


def test_sync_notebook(tmp_path: Path):
    blpath = tmp_path / 'bline.txt'
    stdin = StringIO()
    stdin.write(NOTEBOOK_LINE1)
    stdin.seek(0)
    code = main(['sync', '--baseline-path', str(blpath)], stdin, StringIO())
    assert code == 0
    actual = blpath.read_text()
    line1 = actual.splitlines()[0]
    assert line1 == 'fail.ipynb:cell_1:0: error: Incompatible return value type (got "int", expected "str")  [return-value]'  # noqa: E501

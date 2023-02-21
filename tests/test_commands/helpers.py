from __future__ import annotations

from io import StringIO

from mypy_baseline import main


LINE1 = 'views.py:69: error: Hello world  [assignment]\r\n'
LINE2 = 'settings.py:42: error: How are you?  [union-attr]\r\n'


def run(cmd: list[str]) -> str:
    stdout = StringIO()
    code = main(cmd, StringIO(), stdout)
    assert code == 0
    stdout.seek(0)
    return stdout.read()

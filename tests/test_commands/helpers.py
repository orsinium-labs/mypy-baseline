from __future__ import annotations

from io import StringIO

from mypy_baseline import main


LINE1 = 'views.py:69: error: Hello world  [assignment]\r\n'
LINE2 = 'settings.py:42: error: How are you?  [union-attr]\r\n'

NOTEBOOK_LINE1 = 'fail.ipynb:cell_1:2: \x1b[1m\x1b[31merror:\x1b(B\x1b[m Incompatible return value type (got \x1b(B\x1b[m\x1b[1m"int"\x1b(B\x1b[m, expected \x1b(B\x1b[m\x1b[1m"str"\x1b(B\x1b[m)  \x1b(B\x1b[m\x1b[33m[return-value]\x1b(B\x1b[m\n'
NOTEBOOK_LINE1_EXPECTED = 'fail.ipynb:cell_1:2: error: Incompatible return value type (got "int", expected "str")  [return-value]'

def run(cmd: list[str], exit_code: int = 0) -> str:
    stdout = StringIO()
    code = main(cmd, StringIO(), stdout)
    stdout.seek(0)
    result = stdout.read()
    assert code == exit_code, result
    return result

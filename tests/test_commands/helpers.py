from __future__ import annotations

from io import StringIO

from mypy_baseline import main


LINE1 = 'views.py:69: error: Hello world  [assignment]\r\n'
LINE2 = 'settings.py:42: error: How are you?  [union-attr]\r\n'
LINE3 = 'python/utils.py:15: error: Second argument of Enum() must be string  [misc]\n'
LINE_WITH_NOTE = 'integrations/services.py:0: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports'  # noqa: E501
SUCCESS_LINE = 'Success: no issues found in 26 source files'
NOTEBOOK_LINE1 = 'fail.ipynb:cell_1:2: \x1b[1m\x1b[31merror:\x1b(B\x1b[m Incompatible return value type (got \x1b(B\x1b[m\x1b[1m"int"\x1b(B\x1b[m, expected \x1b(B\x1b[m\x1b[1m"str"\x1b(B\x1b[m)  \x1b(B\x1b[m\x1b[33m[return-value]\x1b(B\x1b[m\n'  # noqa: E501


def run(cmd: list[str], exit_code: int = 0) -> str:
    stdout = StringIO()
    code = main(cmd, StringIO(), stdout)
    stdout.seek(0)
    result = stdout.read()
    assert code == exit_code, result
    return result

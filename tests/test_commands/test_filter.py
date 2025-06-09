from __future__ import annotations

from io import StringIO

from mypy_baseline import main

from .helpers import (
    ERROR_HIGHLIGHT, INDICATION_LINE, LINE1, LINE2, LINE3, LINE_WITH_NOTE, NOTEBOOK_LINE1, SUCCESS_LINE, run,
)


def test_filter():
    stdin = StringIO()
    stdin.write(LINE1)
    stdin.write(INDICATION_LINE)
    stdin.write(ERROR_HIGHLIGHT)
    stdin.write(LINE2)
    stdin.write(LINE3)
    stdin.write(LINE_WITH_NOTE)
    stdin.seek(0)
    stdout = StringIO()
    code = main(['filter'], stdin, stdout)
    assert code == 4
    actual = stdout.getvalue()
    assert LINE1.strip() in actual
    # Ensure the context is not removed by default
    assert INDICATION_LINE in actual
    assert ERROR_HIGHLIGHT in actual

    assert LINE2.strip() in actual
    assert LINE3.strip() in actual
    assert LINE_WITH_NOTE.strip() in actual
    assert '  assignment  ' in actual
    assert '  union-attr  ' in actual
    assert '  unresolved' in actual
    assert ' note ' in actual
    assert 'Your changes introduced' in actual


def test_filter__ignore_category():
    stdin = StringIO()
    stdin.write(LINE_WITH_NOTE)
    stdin.seek(0)
    stdout = StringIO()
    code = main(['filter', '--ignore-categories', 'note'], stdin, stdout)
    assert code == 0
    actual = stdout.getvalue()
    assert actual == ''


def test_filter__ignore():
    stdin = StringIO()
    stdin.write(LINE3)
    stdin.seek(0)
    stdout = StringIO()
    code = main(['filter', '--ignore', '.*Enum.*'], stdin, stdout)
    assert code == 0
    actual = stdout.getvalue()
    assert actual == ''


def test_filter_notebook():
    stdin = StringIO()
    stdin.write(NOTEBOOK_LINE1)

    stdin.seek(0)
    stdout = StringIO()
    code = main(['filter'], stdin, stdout)
    assert code == 1
    actual = stdout.getvalue()
    assert NOTEBOOK_LINE1 in actual
    assert '  return-value  ' in actual
    assert '  unresolved' in actual
    assert 'Your changes introduced' in actual


def test_filter__empty_stdin():
    actual = run(['filter'])
    assert actual == ''


def test_filter__ignore_non_errors():
    stdin = StringIO()
    stdin.write(LINE1)
    stdin.write(INDICATION_LINE)
    stdin.write(ERROR_HIGHLIGHT)
    stdin.seek(0)
    stdout = StringIO()
    code = main(['filter', '--ignore-non-errors'], stdin, stdout)
    assert code == 1
    actual = stdout.getvalue()
    assert INDICATION_LINE not in actual
    assert ERROR_HIGHLIGHT not in actual
    assert LINE1 in actual

def test_filter_success():
    stdin = StringIO()
    stdin.write(SUCCESS_LINE)
    stdin.seek(0)
    stdout = StringIO()
    code = main(['filter'], stdin, stdout)
    assert code == 0
    actual = stdout.getvalue()
    assert actual == SUCCESS_LINE

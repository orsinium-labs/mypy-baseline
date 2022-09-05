from pathlib import Path
from mypy_baseline import main
from io import StringIO


def test_version():
    stdout = StringIO()
    code = main(['version'], StringIO(), stdout)
    assert code == 0
    stdout.seek(0)
    actual = stdout.read()
    assert actual.count('.') == 2


LINE1 = 'views.py:69: error: Hello world  [assignment]\r\n'
LINE2 = 'settings.py:42: error: How are you?  [union-attr]\r\n'


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


def test_filter():
    stdin = StringIO()
    stdin.write(LINE1)
    stdin.write(LINE2)
    stdin.seek(0)
    stdout = StringIO()
    code = main(['filter'], stdin, stdout)
    assert code == 2
    stdout.seek(0)
    actual = stdout.read()
    assert LINE1.strip() in actual
    assert LINE2.strip() in actual
    assert '  assignment  ' in actual
    assert '  union-attr  ' in actual
    assert '  unresolved' in actual
    assert 'Your changes introduced' in actual
    assert 'top files with errors' in actual


def test_filter__empty_stdin():
    stdin = StringIO()
    stdout = StringIO()
    code = main(['filter'], stdin, stdout)
    assert code == 0
    stdout.seek(0)
    actual = stdout.read()
    assert actual == ''

from io import StringIO
from pathlib import Path

from mypy_baseline import main


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


def test_filter__empty_stdin():
    stdin = StringIO()
    stdout = StringIO()
    code = main(['filter'], stdin, stdout)
    assert code == 0
    stdout.seek(0)
    actual = stdout.read()
    assert actual == ''


def test_top_files(tmp_path: Path):
    blpath = tmp_path / 'bline.txt'
    blpath.write_text(f'{LINE1}{LINE2}')
    cmd = ['top-files', '--baseline-path', str(blpath), '--no-color']
    stdout = StringIO()
    code = main(cmd, StringIO(), stdout)
    assert code == 0
    stdout.seek(0)
    actual = stdout.read()
    assert 'views.py' in actual
    assert 'settings.py' in actual


def test_history():
    readme_path = Path(__file__).parent.parent / 'README.md'
    cmd = ['history', '--baseline-path', str(readme_path), '--no-color']
    stdout = StringIO()
    code = main(cmd, StringIO(), stdout)
    assert code == 0
    stdout.seek(0)
    actual = stdout.read()
    exp = '2022-09-01 11:45:28+02:00  60 =   3   -1  +58   8fe7afd10c  git@orsinium.dev'
    assert exp in actual

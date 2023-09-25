from __future__ import annotations

from pathlib import Path

from .helpers import run


def test_history(request):
    readme_path = Path(request.config.rootdir, 'README.md')
    cmd = ['history', '--baseline-path', str(readme_path), '--no-color']
    actual = run(cmd)
    exp = '2022-09-01 11:45:28+02:00  60 =   3   -1  +58   8fe7afd10c  git@orsinium.dev'
    assert exp in actual

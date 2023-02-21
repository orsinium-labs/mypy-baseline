from __future__ import annotations

import os
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .helpers import LINE1, run


@contextmanager
def enter_dir(path: Path) -> Iterator[None]:
    old_path = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_path)


def run_git(*args):
    subprocess.run(['git', *args]).check_returncode()


def test_suggest(tmp_path: Path):
    repo_path = tmp_path / 'repo'
    repo_path.mkdir()
    with enter_dir(repo_path):
        run_git('init')
        bline_path = repo_path / 'baseline.txt'
        bline_path.write_text(LINE1)
        run_git('add', str(bline_path))
        run_git('commit', '-m', 'init')
        run_git('checkout', '-b', 'feature-branch')
        cmd = ['suggest', '--baseline-path', str(bline_path)]
        stdout = run(cmd, exit_code=1)
        assert LINE1.strip() == stdout.strip()

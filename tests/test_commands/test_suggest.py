from __future__ import annotations

import os
import subprocess
from argparse import ArgumentParser
from contextlib import contextmanager
from io import StringIO
from pathlib import Path
from typing import Iterator

import pytest
from responses import RequestsMock

from mypy_baseline._config import Config
from mypy_baseline.commands import Suggest

from .helpers import LINE1, LINE2, run


@contextmanager
def enter_dir(path: Path) -> Iterator[None]:
    old_path = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_path)


@contextmanager
def set_env_vars(env_vars: dict[str, str]) -> Iterator[None]:
    old = os.environ.copy()
    try:
        os.environ.update(env_vars)
        yield
    finally:
        os.environ.clear()
        os.environ.update(old)


def run_git(*args):
    subprocess.run(['git', *args]).check_returncode()


@pytest.fixture
def repo_path(tmp_path: Path) -> Iterator[Path]:
    repo_path = tmp_path / 'repo'
    repo_path.mkdir()
    with enter_dir(repo_path):
        run_git('init')
        yield repo_path


def test_suggest(repo_path: Path):
    bline_path = repo_path / 'baseline.txt'
    bline_path.write_text(LINE1)
    run_git('add', str(bline_path))
    run_git('commit', '-m', 'init')
    run_git('checkout', '-b', 'feature-branch')
    cmd = ['suggest', '--baseline-path', str(bline_path)]
    stdout = run(cmd, exit_code=1)
    assert stdout.strip() == LINE1.strip()


def test_fixed_and_committed(repo_path: Path):
    """If there are committed fixes in the baseline, don't suggest.
    """
    bline_path = repo_path / 'baseline.txt'
    bline_path.write_text(f'{LINE1}\n{LINE2}')
    run_git('add', str(bline_path))
    run_git('commit', '-m', 'init')
    run_git('checkout', '-b', 'feature-branch')
    bline_path.write_text(LINE1)
    run_git('commit', '-am', 'fix bline')
    cmd = ['suggest', '--baseline-path', str(bline_path)]
    stdout = run(cmd, exit_code=0)
    assert stdout.strip() == ''


def test_target_branch__cli_flag():
    parser = ArgumentParser()
    Config.init_parser(parser)
    args = parser.parse_args(['--default-branch', 'something'])
    cmd = Suggest(args=args, stdin=StringIO(), stdout=StringIO())
    assert cmd.target == 'something'


@pytest.mark.parametrize('env_var', [
    'CI_MERGE_REQUEST_TARGET_BRANCH_SHA',
    'GITHUB_BASE_REF',
])
def test_target_branch__env_var(env_var: str):
    parser = ArgumentParser()
    Config.init_parser(parser)
    args = parser.parse_args([])
    with set_env_vars({env_var: 'something'}):
        cmd = Suggest(args=args, stdin=StringIO(), stdout=StringIO())
        assert cmd.target == 'something'


def test_comment():
    parser = ArgumentParser()
    Suggest.init_parser(parser)
    args = parser.parse_args([])
    cmd = Suggest(args=args, stdin=StringIO(), stdout=StringIO())
    env_vars = dict(
        CI_API_V4_URL='https://gitlab.example.com/api/v4/',
        CI_MERGE_REQUEST_PROJECT_ID='123',
        CI_MERGE_REQUEST_IID='456',
        GITLAB_API_TOKEN='glab-789',
        GITLAB_CI='yes',
    )
    with RequestsMock() as responses:
        responses.get(
            'https://gitlab.example.com/api/v4//projects/123/merge_requests/456/notes',
            json=[],
        )
        responses.post(
            'https://gitlab.example.com/api/v4//projects/123/merge_requests/456/notes',
        )
        with set_env_vars(env_vars):
            cmd._post_to_gitlab('oh hi mark')

from __future__ import annotations

import os
import random
import subprocess
from argparse import ArgumentParser
from functools import cached_property
from pathlib import Path
from typing import Iterable

from .._error import Error
from ._base import Command


TARGET_BRANCH_ENV_VARS = (
    # GitLab CI
    'CI_MERGE_REQUEST_TARGET_BRANCH_SHA',
    # GitHub Actions
    'GITHUB_BASE_REF',
)
PR_ID_ENV_VARS = (
    # GitLab CI
    'CI_MERGE_REQUEST_ID',
    # GitHub Actions
    'GITHUB_REF_NAME',
)


class Suggest(Command):
    """Suggest to fix a violation from the baseline.
    """

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        Command.init_parser(parser)
        parser.add_argument(
            '--seed',
            help='seed to use when randomly picking a suggestion',
        )
        parser.add_argument(
            '--min-fixed', default=1,
            help='required number of fixes for the MR',
        )
        parser.add_argument(
            '--exit-zero', action='store_true',
            help='always return zero exit code',
        )

    def run(self) -> int:
        if self.fixed_count >= self.args.min_fixed:
            return 0
        self.print(self.suggested.raw_line)
        if self.args.exit_zero:
            return 0
        return 1

    @cached_property
    def target(self) -> str:
        """Get the target branch/commit reference for this PR.
        """
        if self.config.default_branch:
            return self.config.default_branch

        # detect default branch from env vars
        for env_var in TARGET_BRANCH_ENV_VARS:
            target = os.environ.get(env_var)
            if target:
                return target

        # detect default branch for the `origin` remote
        # (may fail if there is no remote)
        try:
            lines = self._get_stdout('symbolic-ref', 'refs/remotes/origin/HEAD')
        except subprocess.CalledProcessError:
            pass
        else:
            return lines[-1].split('/')[-1]

        # try well-known branch names
        for branch_name in ('main', 'master', 'develop'):
            res = subprocess.run(
                ['git', 'rev-parse', '--verify', branch_name],
                stdout=subprocess.DEVNULL,
            )
            if res.returncode == 0:
                return branch_name
        raise LookupError('cannot detect default branch name')

    @cached_property
    def fixed_count(self) -> int:
        """Get number of baseline violations fixed in this PR.
        """
        lines = self._get_stdout(
            'diff', 'HEAD', self.target, '--',
            str(self.config.baseline_path),
        )
        count = 0
        for line in lines:
            if line.startswith('-') and not line.startswith('---'):
                count += 1
        return count

    @cached_property
    def changed_files(self) -> tuple[Path, ...]:
        """Get all lines changed in this PR.
        """
        lines = self._get_stdout('diff', '--name-only', self.target)
        return tuple(Path(line).absolute() for line in lines)

    def _get_stdout(self, *args: str) -> list[str]:
        """Run the command in the shell and get stdout lines.
        """
        result = subprocess.run(['git', *args], stdout=subprocess.PIPE)
        result.check_returncode()
        stdout = result.stdout.decode().strip()
        return stdout.splitlines()

    @property
    def suggested(self) -> Error:
        """Pick a violation that shoud be suggested to fix.
        """
        errors = [e for e in self.baseline if e.severity == 'error']
        if not errors:
            errors = self.baseline
        # pick an error in one of the changed files
        for error in errors:
            if error.path.absolute() in self.changed_files:
                return error
        # pick a random error
        random.seed(self.seed)
        return random.choice(errors)

    @cached_property
    def baseline(self) -> list[Error]:
        """Parse errors from the baseline.
        """
        baseline: list[Error] = []
        for line in self.baseline_lines:
            err = Error.new(line)
            if err is not None:
                baseline.append(err)
        if not baseline:
            raise RuntimeError('baseline is empty')
        return baseline

    @property
    def baseline_lines(self) -> Iterable[str]:
        """Read baseline and return lines of it, one per violation.
        """
        # if not self.stdin.isatty():
        #     return self.stdin
        text = self.config.baseline_path.read_text(encoding='utf8')
        return text.splitlines()

    @cached_property
    def seed(self) -> str:
        """Get the seed to init randomizer.

        If `--seed` is not specified, try to pick value
        so that it's always the same for the same MR
        but different for different MRs.
        """
        if self.args.seed:
            return self.args.seed
        for env_var in PR_ID_ENV_VARS:
            pr_id = os.environ.get(env_var)
            if pr_id:
                return pr_id
        return ''

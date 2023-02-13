from __future__ import annotations
from functools import cached_property
import os
from pathlib import Path
import random
import subprocess

from ._base import Command
from .._error import Error


class Suggest(Command):
    """Suggest which baselined violations to fix.
    """

    def run(self) -> int:
        if self.fixes_count:
            return 0
        print(self.suggested.raw_line)
        return 1

    @cached_property
    def target(self) -> str:
        """Get the target branch/commit reference for this PR.
        """
        target = os.environ.get('CI_MERGE_REQUEST_TARGET_BRANCH_SHA')
        if target:
            return target

        cmd = ['git', 'symbolic-ref', 'refs/remotes/origin/HEAD']
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        result.check_returncode()
        stdout = result.stdout.decode().strip()
        default_branch = stdout.split('/')[-1]
        return default_branch

    @cached_property
    def fixes_count(self) -> int:
        """Get number of baseline violations fixed in this PR.
        """
        lines = self._get_stdout(
            'git', 'diff',
            'HEAD', self.target,
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
        lines = self._get_stdout('git', 'diff', '--name-only', self.target)
        return tuple(Path(line).absolute() for line in lines)

    def _get_stdout(self, *cmd: str) -> list[str]:
        """Run the command in the shell and get stdout lines.
        """
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        result.check_returncode()
        stdout = result.stdout.decode().strip()
        return stdout.splitlines()

    @property
    def suggested(self) -> Error:
        # pick an error in one of the changed files
        for error in self.baseline:
            if error.path.absolute() in self.changed_files:
                return error
        # pick a random error
        random.seed(13)
        return random.choice(self.baseline)

    @cached_property
    def baseline(self) -> list[Error]:
        text = self.config.baseline_path.read_text(encoding='utf8')
        lines = text.splitlines()
        baseline: list[Error] = []
        for line in lines:
            err = Error.new(line)
            if err:
                baseline.append(err)
        return baseline

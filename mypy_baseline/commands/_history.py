from __future__ import annotations

from .._git import get_commits
from ._base import Command


class History(Command):
    """Show how the baseline changed over time.
    """

    def run(self) -> int:
        prev_count = 0
        self.print('date       time           res   old  fix  new')
        for commit in get_commits(self.config.baseline_path):
            count_formatted = f'{commit.lines_count:>3}'
            line = f'{commit.created_at} {self.colors.blue(count_formatted)}'
            line += self.colors.gray(f' = {prev_count:>3}')
            if commit.deletions:
                formatted = f'{-commit.deletions: >+4}'
                line += f' {self.colors.green(formatted)}'
            else:
                line += ' ' * 5
            if commit.insertions:
                formatted = f'{commit.insertions: >+4}'
                line += f' {self.colors.red(formatted)}'
            self.print(line)
            prev_count = commit.lines_count
        return 0

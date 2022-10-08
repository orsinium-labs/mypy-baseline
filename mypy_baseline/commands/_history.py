from __future__ import annotations

from .._git import get_commits
from ._base import Command


class History(Command):
    """Show how the baseline changed over time.
    """

    def run(self) -> int:
        prev_count: int | None = None
        self.print('date       time           res   old  fix  new   commit      author')
        for commit in get_commits(self.config.baseline_path):
            commit.fix_lines_count(prev_count)
            count_formatted = f'{commit.lines_count:>3}'
            line = f'{commit.created_at} {self.colors.blue(count_formatted)}'
            line += f' = {prev_count or 0:>3}'
            if commit.deletions:
                formatted = f'{-commit.deletions: >+4}'
                line += f' {self.colors.green(formatted)}'
            else:
                line += ' ' * 5
            if commit.insertions:
                formatted = f'{commit.insertions: >+4}'
                line += f' {self.colors.red(formatted)}'
            else:
                line += ' ' * 5
            line += f'   {commit.hash[:10]}'
            line += f'  {self.colors.magenta(commit.author_email)}'
            self.print(line)
            prev_count = commit.lines_count
        return 0

from __future__ import annotations

import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import Iterator


REX_COMMIT = re.compile(
    (
        r'(?P<hash>[0-9a-f]{40}) '
        r'(?P<created_at>[0-9T:+-]+)\s+'
        r'(?P<author_email>[^\s]+)\s+'
        r'.+ \| \d+ [+-]+\s+'
        r'\d+ files? changed'
        r'(?:, (?P<insertions>\d+) insertions?\(\+\))?'
        r'(?:, (?P<deletions>\d+) deletions?\(\-\))?'
    ),
    re.MULTILINE
)


@dataclass
class Commit:
    path: Path
    hash: str
    author_email: str
    created_at: datetime
    insertions: int
    deletions: int

    @cached_property
    def lines_count(self) -> int:
        path = self.path
        if path.is_absolute():
            path = path.relative_to(Path().absolute())
        cmd = ['git', 'show', f'{self.hash}:{path}']
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        result.check_returncode()
        lines = result.stdout.decode().strip().splitlines()
        return len(lines)

    def fix_lines_count(self, prev_count: int | None) -> None:
        """
        We want to show not the actual lines count that the commit resulted in
        but how its changed affected the previous count.
        These numbers can be different if there are 2 commits with the same
        parent commit that changed the baseline.
        """
        if prev_count is not None:
            self.lines_count = prev_count + self.insertions - self.deletions

    def as_dict(self) -> dict[str, object]:
        result = asdict(self)
        result['lines_count'] = self.lines_count
        return result


def get_commits(path: Path) -> Iterator[Commit]:
    cmd = ['git', 'log', '--format=%H %cI %ae', '--reverse', '--stat', '--', str(path)]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    result.check_returncode()
    stdout = result.stdout.decode()
    for match in REX_COMMIT.finditer(stdout):
        info = match.groupdict()
        yield Commit(
            path=path,
            hash=info['hash'],
            author_email=info['author_email'],
            created_at=datetime.fromisoformat(info['created_at']),
            insertions=int(info['insertions'] or '0'),
            deletions=int(info['deletions'] or '0'),
        )

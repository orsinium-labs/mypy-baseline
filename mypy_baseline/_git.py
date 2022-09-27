from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import subprocess
from typing import Iterator

REX_COMMIT = re.compile(
    (
        r'(?P<hash>[0-9a-f]{40}) '
        r'(?P<created_at>[0-9T:+-]+)\s+'
        r'.+ \| \d+ [+-]+\s+'
        r'\d+ files? changed'
        r'(?:, (?P<insertions>\d+) insertions?\(\+\))?'
        r'(?:, (?P<deletions>\d+) deletions?\(\-\))?'
    ),
    re.MULTILINE
)


@dataclass
class Commit:
    hash: str
    created_at: datetime
    insertions: int
    deletions: int


def get_commits(path: Path) -> Iterator[Commit]:
    cmd = ['git', 'log', '--format=%H %cI', '--stat', '--', str(path)]
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    result.check_returncode()
    stdout = result.stdout.decode()
    for match in REX_COMMIT.finditer(stdout):
        info = match.groupdict()
        yield Commit(
            hash=info['hash'],
            created_at=datetime.fromisoformat(info['created_at']),
            insertions=int(info['insertions'] or '0'),
            deletions=int(info['deletions'] or '0'),
        )

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ._config import Config

COLOR_PATTERN = '(\x1b\\[\\d*m?|\x0f)*'
REX_COLOR = re.compile(COLOR_PATTERN)
REX_LINE = re.compile(rf"""
    (?P<path>.+\.py):
    (?P<lineno>[0-9]+):\s
    {COLOR_PATTERN}(?P<severity>[a-z]+):{COLOR_PATTERN}\s
    (?P<message>.+?)
    (?:\s\s{COLOR_PATTERN}\[(?P<category>[a-z-]+)\]{COLOR_PATTERN})?
    \s*
""", re.VERBOSE | re.MULTILINE)


@dataclass
class Error:
    raw_line: str
    _match: re.Match

    @classmethod
    def new(self, line: str) -> Error | None:
        match = REX_LINE.fullmatch(line)
        if match is None:
            return None
        return Error(line, match)

    @cached_property
    def path(self) -> Path:
        return Path(self._match.group('path'))

    @cached_property
    def line_number(self) -> int:
        result = int(self._match.group('lineno'))
        assert result >= 0
        return result

    @cached_property
    def severity(self) -> str:
        return self._match.group('severity')

    @cached_property
    def message(self) -> str:
        return self._match.group('message')

    @cached_property
    def category(self) -> str:
        return self._match.group('category') or 'note'

    def get_clean_line(self, config: Config) -> str:
        path = Path(*self.path.parts[:config.depth])
        pos = self.line_number if config.preserve_position else 0
        msg = REX_COLOR.sub('', self.message).strip()
        line = f'{path}:{pos}: {self.severity}: {msg}'
        if self.category != 'note':
            line += f'  [{self.category}]'
        return line

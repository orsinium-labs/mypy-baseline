from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ._config import Config

REX_COLOR = re.compile('(\x1b\\[\\d*m?|\x0f)*')
REX_COLOR_NBQA = re.compile(r'\[\d*\x1bm|\x1b|\(B')
REX_LINE = re.compile(r"""
    (?P<path>.+\.pyi?):
    (?P<lineno>[0-9]+):\s
    (?P<severity>[a-z]+):\s
    (?P<message>.+?)
    (?:\s\s\[(?P<category>[a-z-]+)\])?
    \s*
""", re.VERBOSE | re.MULTILINE)
REX_LINE_NBQA = re.compile(r"""
    (?P<path>.+\.ipynb:cell_[0-9]+):
    (?P<lineno>[0-9]+):\s
    (?P<severity>[a-z]+):\s
    (?P<message>.+?)
    (?:\s\s\[(?P<category>[a-z-]+)\])?
    \s*
""", re.VERBOSE | re.MULTILINE)
REX_LINE_IN_MSG = re.compile(r'defined on line \d+')


def _remove_color_codes(line: str) -> str:
    line = REX_COLOR.sub('', line)
    return REX_COLOR_NBQA.sub('', line)


@dataclass
class Error:
    raw_line: str
    _match: re.Match[str]

    @classmethod
    def new(self, line: str) -> Error | None:
        line = _remove_color_codes(line)
        match = REX_LINE.fullmatch(line) or REX_LINE_NBQA.fullmatch(line)
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
        msg = REX_COLOR_NBQA.sub('', msg).strip()
        msg = REX_LINE_IN_MSG.sub('defined on line 0', msg)
        line = f'{path}:{pos}: {self.severity}: {msg}'
        if self.category != 'note':
            line += f'  [{self.category}]'
        return line

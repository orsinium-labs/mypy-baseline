from __future__ import annotations

import dataclasses
import os
import re
from argparse import ArgumentParser
from functools import cached_property
from pathlib import Path
from typing import Any


try:
    import toml
except ImportError:
    toml = None  # type: ignore[assignment]
try:
    import tomli
except ImportError:
    # https://peps.python.org/pep-0680/
    try:
        import tomllib as tomli  # type: ignore
    except ImportError:
        tomli = None  # type: ignore[assignment]


@dataclasses.dataclass
class Config:
    baseline_path: Path = Path('mypy-baseline.txt')
    depth: int = 40
    allow_unsynced: bool = False
    preserve_position: bool = False
    hide_stats: bool = False
    no_colors: bool = bool(os.environ.get('NO_COLOR'))
    ignore: list[str] = dataclasses.field(default_factory=list)
    ignore_categories: list[str] = dataclasses.field(default_factory=list)
    default_branch: str = ''

    @classmethod
    def from_args(cls, args: dict[str, Any]) -> Config:
        config = cls()
        config = config.read_file(args['config'])
        config = config.read_args(args)
        if isinstance(config.baseline_path, str):
            config.baseline_path = Path(config.baseline_path)
        return config

    @classmethod
    def init_parser(self, parser: ArgumentParser) -> None:
        add = parser.add_argument
        add(
            '--config', type=Path, default=Path('pyproject.toml'),
            help='path to the configuration file.'
        )
        add(
            '--baseline-path', type=Path,
            help='path to the file where to store baseline.',
        )
        add(
            '--depth', type=int,
            help='cut paths longer than that many directories deep.'
        )

        add(
            '--allow-unsynced', action='store_true',
            help='do not fail for resolved violations.'
        )
        add(
            '--preserve-position', action='store_true',
            help='do not remove line number from the baseline.',
        )
        add(
            '--hide-stats', action='store_true',
            help='do not show stats at the end.',
        )
        add(
            '--no-colors', action='store_true',
            help='disable colored output. Has no effect on the output of mypy.',
        )
        add(
            '--ignore', nargs='*',
            help='regexes for messages to ignore, e.g. ".*Enum.*"',
        )
        add(
            '--ignore-categories', nargs='*',
            help='categories of mypy errors to ignore, e.g. "note" or "call-arg"',
        )
        add(
            '--default-branch',
            help='default git branch name.',
        )

    def read_file(self, path: Path) -> Config:
        if not path.exists():
            return self

        # parse the config file
        if tomli is not None:
            with path.open('rb') as stream:
                data = tomli.load(stream)
        elif toml is not None:
            with path.open('rb', encoding='utf8') as stream:
                data = dict(toml.load(stream))
        else:
            return self

        # extract the right section from the config
        try:
            data = data['tool']['mypy-baseline']
        except KeyError:
            try:
                data = data['tool']['mypy_baseline']
            except KeyError:
                return self
        return dataclasses.replace(self, **data)

    def read_args(self, args: dict[str, Any]) -> Config:
        config = dataclasses.replace(self)
        for field in dataclasses.fields(self):
            value = args[field.name]
            if value is not None:
                setattr(config, field.name, value)
        return config

    @cached_property
    def _ignore_regexes(self) -> list[re.Pattern[str]]:
        result = []
        assert isinstance(self.ignore, list)
        for pattern in self.ignore:
            try:
                result.append(re.compile(pattern))
            except re.error:
                raise ValueError(f'Invalid pattern: {pattern}')
        return result

    def is_ignored(self, msg: str) -> bool:
        """Check if the message matches any ignore pattern from the config.
        """
        return any(rex.fullmatch(msg) for rex in self._ignore_regexes)

    def is_ignored_category(self, category: str) -> bool:
        """Check if the category matches any ignore pattern from the config.
        """
        return category in self.ignore_categories

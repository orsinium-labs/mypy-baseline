from __future__ import annotations

from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar, TextIO

from .._colors import Colors
from .._config import Config


@dataclass
class Command:
    name: ClassVar[str]
    args: Namespace
    stdin: TextIO
    stdout: TextIO

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        Config.init_parser(parser)

    def run(self) -> int:
        raise NotImplementedError

    def print(self, *args: str, end='\n', sep=' ') -> None:
        print(*args, file=self.stdout, end=end, sep=sep)

    @cached_property
    def config(self) -> Config:
        return Config.from_args(vars(self.args))

    @cached_property
    def colors(self) -> Colors:
        return Colors(disabled=self.config.no_colors)

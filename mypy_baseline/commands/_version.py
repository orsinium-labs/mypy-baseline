from __future__ import annotations
from ._base import Command


class Version(Command):
    def run(self) -> int:
        from mypy_baseline import __version__
        self.print(__version__)
        return 0

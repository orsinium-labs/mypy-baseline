from __future__ import annotations

from types import MappingProxyType

from ._base import Command
from ._filter import Filter
from ._history import History
from ._plot import Plot
from ._sync import Sync
from ._version import Version


commands: MappingProxyType[str, type[Command]]
commands = MappingProxyType(dict(
    filter=Filter,
    history=History,
    plot=Plot,
    sync=Sync,
    version=Version,
))

__all__ = [
    'commands',
    'Command',
]

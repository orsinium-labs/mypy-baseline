from __future__ import annotations
from types import MappingProxyType
from ._base import Command
from ._version import Version
from ._sync import Sync
from ._filter import Filter

commands: MappingProxyType[str, type[Command]]
commands = MappingProxyType(dict(
    filter=Filter,
    sync=Sync,
    version=Version,
))

__all__ = [
    'commands',
    'Command',
]

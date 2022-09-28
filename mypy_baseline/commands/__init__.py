from __future__ import annotations

from types import MappingProxyType

from ._base import Command
from ._filter import Filter
from ._history import History
from ._plot import Plot
from ._sync import Sync
from ._top_files import TopFiles
from ._version import Version


commands: MappingProxyType[str, type[Command]]
commands = MappingProxyType({
    'filter': Filter,
    'history': History,
    'plot': Plot,
    'sync': Sync,
    'top-files': TopFiles,
    'version': Version,
})

__all__ = [
    'commands',
    'Command',
]

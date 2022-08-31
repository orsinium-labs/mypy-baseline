from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    baseline_path: Path = Path('mypy-baseline.txt')
    depth: int = 40
    allow_unsynced: bool = False
    preserve_position: bool = False
    hide_stats: bool = False
    no_colors: bool = False

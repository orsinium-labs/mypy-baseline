from __future__ import annotations

from .._error import Error
from ._base import Command


class Sync(Command):
    """Generate baseline with all existing errors.
    """

    def run(self) -> int:
        baseline: list[str] = []
        for line in self.stdin:
            error = Error.new(line)
            if error is None:
                self.print(line, end='')
                continue
            clean_line = error.get_clean_line(self.config)
            baseline.append(clean_line)
        serialized = '\n'.join(baseline) + '\n'
        self.config.baseline_path.write_text(serialized, encoding='utf8')
        return 0

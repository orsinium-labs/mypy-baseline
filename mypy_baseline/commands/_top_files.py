from __future__ import annotations
from argparse import ArgumentParser

from collections import defaultdict

from .._error import Error
from ._base import Command


class TopFiles(Command):
    """Show files with the most errors.
    """
    @classmethod
    def init_parser(cls, parser: ArgumentParser) -> None:
        super().init_parser(parser)
        parser.add_argument(
            '-n', type=int, default=20,
            help='how many files to show',
        )

    def run(self) -> int:
        baseline_text = self.config.baseline_path.read_text(encoding='utf8')
        file_stats: dict[str, int] = defaultdict(int)
        baseline = baseline_text.strip().splitlines()
        for line in baseline:
            error = Error.new(line)
            if error is None:
                self.print(f'cannot parse line: {line}')
                return 1
            path = '/'.join(error.path.parts[:self.config.depth])
            file_stats[path] += 1

        sorted_file_stats = sorted(
            file_stats.items(),
            key=lambda x: x[::-1],
            reverse=True,
        )
        max_width = max(len(path) for path, _ in sorted_file_stats[:self.args.n])
        for path, total_count in sorted_file_stats[:self.args.n]:
            total_formatted = f'{total_count:>3}'
            path = path.ljust(max_width)
            percent = round(total_count / len(baseline) * 100, 1)
            self.print(f'{path} {self.colors.blue(total_formatted)} {percent:>4}%')

        return 0

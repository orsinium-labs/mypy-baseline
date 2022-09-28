from __future__ import annotations

from collections import defaultdict

from .._error import Error
from ._base import Command


class Filter(Command):
    """Filter out old mypy errors from stdin.
    """

    def run(self) -> int:
        try:
            baseline_text = self.config.baseline_path.read_text(encoding='utf8')
        except FileNotFoundError:
            baseline_text = ''
        baseline = baseline_text.splitlines()

        unresolved_errors: list[Error] = []
        new_errors: list[Error] = []

        for line in self.stdin:
            error = Error.new(line)
            if error is None:
                self.print(line, end='')
                continue
            clean_line = error.get_clean_line(self.config)
            try:
                baseline.remove(clean_line)
            except ValueError:
                self.print(line, end='')
                new_errors.append(error)
            else:
                unresolved_errors.append(error)

        fixed_errors: list[Error] = []
        for line in baseline:
            error = Error.new(line)
            if error is None:
                print(f'invalid baseline, cannot parse line: {line}')
                return 1
            fixed_errors.append(error)

        fixed_count = len(fixed_errors)
        new_count = len(new_errors)
        unresolved_count = len(unresolved_errors)

        # calculate exit code
        if not fixed_count and not new_count and not unresolved_count:
            return 0
        exit_code = new_count
        if not self.config.allow_unsynced:
            exit_code += fixed_count
        if exit_code > 100:
            exit_code = 100
        if self.config.hide_stats:
            return exit_code

        # print short summary
        self.print()
        self.print('total errors:')
        self.print(f'  fixed: {self.colors.green(fixed_count)}')
        self.print(f'  new: {self.colors.red(new_count)}')
        self.print(f'  unresolved: {self.colors.blue(unresolved_count)}')
        self.print()

        # print stats for each error code (category)
        stats_total: defaultdict[str, int] = defaultdict(int)
        stats_fixed: defaultdict[str, int] = defaultdict(int)
        stats_new: defaultdict[str, int] = defaultdict(int)
        for error in fixed_errors:
            stats_total[error.category] += 1
            stats_fixed[error.category] += 1
        for error in new_errors:
            stats_total[error.category] += 1
            stats_new[error.category] += 1
        for error in unresolved_errors:
            stats_total[error.category] += 1
        self.print('errors by error code:')
        sorted_stats = sorted(
            stats_total.items(),
            key=lambda x: x[::-1],
            reverse=True,
        )
        for category, total in sorted_stats:
            total_formatted = f'{total: >3}'
            line = f'  {category:24} {self.colors.blue(total_formatted)}'
            fixed = stats_fixed[category]
            if fixed:
                fixed_formatted = f'{-fixed: >3}'
                line += f' {self.colors.green(fixed_formatted)}'
            new = stats_new[category]
            if new:
                new_formatted = f'{new: >+3}'
                line += f' {self.colors.red(new_formatted)}'
            self.print(line)
        self.print()

        msg = self.colors.get_exit_message(fixed=fixed_count, new=new_count)
        self.print(msg)
        return exit_code

from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from itertools import chain
from typing import Any, Callable, TextIO
from ._config import Config
from ._error import Error

RED = '\033[31m'
GREEN = '\033[32m'
BLUE = '\033[94m'
END = '\033[0m'

NEW_ERRORS = """
    ┌────────────────────────────────────────────┄┄
    │ {red}Your changes introduced new violations.{end}
    │ Please, resolve the violations above before moving forward.
    │ Mypy is your friend.
    └────────────────────────────────────────────┄┄
"""
FIXED_ERRORS = """
    ┌────────────────────────────────────────────┄┄
    │ {green}Your changes resolved existing violations.{end}
    │ Great work! Please, run `mypy --show-codes | mypy-baseline sync`
    │ to remove resolved violations from the baseline file.
    └────────────────────────────────────────────┄┄
"""

Command = Callable[[Config, TextIO, TextIO], int]


@dataclass
class Colors:
    disabled: bool

    def green(self, text: Any) -> str:
        if self.disabled:
            return str(text)
        return f'{GREEN}{text}{END}'

    def red(self, text: Any) -> str:
        if self.disabled:
            return str(text)
        return f'{RED}{text}{END}'

    def blue(self, text: Any) -> str:
        if self.disabled:
            return str(text)
        return f'{BLUE}{text}{END}'

    def get_exit_message(self, fixed: int, new: int) -> str:
        if new:
            msg = NEW_ERRORS
        elif fixed:
            msg = FIXED_ERRORS
        else:
            return ''
        if self.disabled:
            red = ''
            green = ''
            end = ''
        else:
            red = RED
            green = GREEN
            end = END
        return msg.format(
            red=red,
            green=green,
            end=end,
        )


def cmd_filter(config: Config, stdin: TextIO, stdout: TextIO) -> int:
    try:
        baseline_text = config.baseline_path.read_text(encoding='utf8')
    except FileNotFoundError:
        baseline_text = ''
    baseline = baseline_text.splitlines()

    unresolved_errors: list[Error] = []
    new_errors: list[Error] = []

    for line in stdin:
        error = Error.new(line)
        if error is None:
            print(line, end='', file=stdout)
            continue
        clean_line = error.get_clean_line(config)
        try:
            baseline.remove(clean_line)
        except ValueError:
            print(line, end='', file=stdout)
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
    if not config.allow_unsynced:
        exit_code += fixed_count
    if exit_code > 100:
        exit_code = 100
    if config.hide_stats:
        return exit_code

    # print short summary
    colors = Colors(disabled=config.no_colors)
    print(file=stdout)
    print('total errors:', file=stdout)
    print(f'  fixed: {colors.green(fixed_count)}', file=stdout)
    print(f'  new: {colors.red(new_count)}', file=stdout)
    print(f'  unresolved: {colors.blue(unresolved_count)}', file=stdout)
    print(file=stdout)

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
    print('errors by error code:', file=stdout)
    sorted_stats = sorted(
        stats_total.items(),
        key=lambda x: x[::-1],
        reverse=True,
    )
    for category, total in sorted_stats:
        total_formatted = f'{total: >3}'
        line = f'  {category:24} {colors.blue(total_formatted)}'
        fixed = stats_fixed[category]
        if fixed:
            fixed_formatted = f'{-fixed: >3}'
            line += f' {colors.green(fixed_formatted)}'
        new = stats_new[category]
        if new:
            new_formatted = f'{new: >+3}'
            line += f' {colors.red(new_formatted)}'
        print(line, file=stdout)
    print(file=stdout)

    # print stats for each file (category)
    print('top files with errors:', file=stdout)
    file_stats: dict[str, int] = defaultdict(int)
    for error in chain(fixed_errors, new_errors, unresolved_errors):
        path = '/'.join(error.path.parts[:config.depth])
        file_stats[path] += 1
    sorted_file_stats = sorted(
        file_stats.items(),
        key=lambda x: x[::-1],
        reverse=True,
    )
    max_width = max(len(path) for path, _ in sorted_file_stats[:5])
    for path, total_count in sorted_file_stats[:5]:
        total_formatted = f'{total_count:>3}'
        path = path.ljust(max_width)
        print(f'  {path} {colors.blue(total_formatted)}', file=stdout)

    msg = colors.get_exit_message(fixed=fixed_count, new=new_count)
    print(msg, file=stdout)
    return exit_code

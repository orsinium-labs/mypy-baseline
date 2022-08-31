from __future__ import annotations
from argparse import ArgumentParser
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Callable, Mapping, NoReturn, TextIO
from ._config import Config
from ._error import Error

RED = '\033[1;31m'
GREEN = '\033[1;32m'
BLUE = '\033[94m'
END = '\033[0m'
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


def cmd_filter(config: Config, stdin: TextIO, stdout: TextIO) -> int:
    baseline_text = config.baseline_path.read_text(encoding='utf8')
    baseline = baseline_text.splitlines()

    fixed_errors: list[Error] = []
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
            fixed_errors.append(error)

    unresolved_errors: list[Error] = []
    for line in baseline:
        error = Error.new(line)
        if error is None:
            print(f'invalid baseline, cannot parse line: {line}')
            return 1
        unresolved_errors.append(error)

    fixed_count = len(fixed_errors)
    new_count = len(new_errors)
    unresolved_count = len(unresolved_errors)

    exit_code = new_count
    if not config.allow_unsynced:
        exit_code += fixed_count
    if exit_code > 100:
        exit_code = 100
    if config.hide_stats:
        return exit_code

    colors = Colors(disabled=config.no_colors)
    print('total errors:', file=stdout)
    print(f'  fixed: {colors.green(fixed_count)}', file=stdout)
    print(f'  new: {colors.red(new_count)}', file=stdout)
    print(f'  unresolved: {colors.blue(unresolved_count)}', file=stdout)
    print(file=stdout)

    stats_total: defaultdict[str, int] = defaultdict()
    stats_fixed: defaultdict[str, int] = defaultdict()
    stats_new: defaultdict[str, int] = defaultdict()
    for error in fixed_errors:
        stats_total[error.category] += 1
        stats_fixed[error.category] += 1
    for error in new_errors:
        stats_total[error.category] += 1
        stats_new[error.category] += 1
    for category, total in sorted(stats_total.items()):
        line = f'{category:10} {total: >3}'
        fixed = stats_fixed[category]
        if fixed:
            fixed_formatted = f'{-fixed:}'
            line += f' {colors.green(fixed_formatted)}'
        new = stats_new[category]
        if new:
            new_formatted = f'{new:+}'
            line += f' {colors.red(new_formatted)}'
        print(line, file=stdout)

    return exit_code


COMMANDS: Mapping[str, Command] = {
    'filter': cmd_filter,
}


def main(argv: list[str], stdin: TextIO, stdout: TextIO) -> int:
    exe = Path(sys.executable).name
    parser = ArgumentParser(f'mypy --show-codes | {exe} -m mypy_baseline')
    parser.add_argument('cmd', default='filter', choices=sorted(COMMANDS))
    Config.init_parser(parser)
    args: dict[str, Any] = parser.parse_args(argv, dict())
    cmd = COMMANDS[args['cmd']]
    config = Config.from_args(args)
    return cmd(config, stdin, stdout)


def entrypoint() -> NoReturn:
    sys.exit(main(sys.argv[1:], sys.stdin, sys.stdout))

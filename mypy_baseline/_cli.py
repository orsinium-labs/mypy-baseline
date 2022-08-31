from __future__ import annotations
from argparse import ArgumentParser
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Callable, Mapping, NoReturn, TextIO
from ._config import Config
from ._error import Error

RED = '\033[31m'
GREEN = '\033[32m'
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
    for category, total in sorted(stats_total.items()):
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

    return exit_code


def cmd_sync(config: Config, stdin: TextIO, stdout: TextIO) -> int:
    baseline: list[str] = []
    for line in stdin:
        error = Error.new(line)
        if error is None:
            print(line, end='', file=stdout)
            continue
        clean_line = error.get_clean_line(config)
        baseline.append(clean_line)
    config.baseline_path.write_text('\n'.join(baseline), encoding='utf8')
    return 0


def cmd_version(config: Config, stdin: TextIO, stdout: TextIO) -> int:
    from mypy_baseline import __version__
    print(__version__, file=stdout)
    return 0


COMMANDS: Mapping[str, Command] = {
    'filter': cmd_filter,
    'sync': cmd_sync,
    'version': cmd_version,
}


def main(argv: list[str], stdin: TextIO, stdout: TextIO) -> int:
    exe = Path(sys.executable).name
    parser = ArgumentParser(f'mypy --show-codes | {exe} -m mypy_baseline')
    parser.add_argument('cmd', choices=sorted(COMMANDS))
    Config.init_parser(parser)
    args = parser.parse_args(argv)
    cmd = COMMANDS[args.cmd]
    config = Config.from_args(vars(args))
    return cmd(config, stdin, stdout)


def entrypoint() -> NoReturn:
    sys.exit(main(sys.argv[1:], sys.stdin, sys.stdout))

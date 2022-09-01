from __future__ import annotations
from argparse import ArgumentParser
import sys
from typing import Callable, Mapping, NoReturn, TextIO
from ._config import Config
from ._error import Error
from ._cmd_filter import cmd_filter

Command = Callable[[Config, TextIO, TextIO], int]


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
    parser = ArgumentParser('mypy --show-codes | mypy-baseline')
    parser.add_argument('cmd', choices=sorted(COMMANDS))
    Config.init_parser(parser)
    args = parser.parse_args(argv)
    cmd = COMMANDS[args.cmd]
    config = Config.from_args(vars(args))
    return cmd(config, stdin, stdout)


def entrypoint() -> NoReturn:
    sys.exit(main(sys.argv[1:], sys.stdin, sys.stdout))

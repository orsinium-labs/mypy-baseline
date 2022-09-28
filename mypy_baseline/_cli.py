from __future__ import annotations

import sys
from argparse import ArgumentParser
from typing import NoReturn, TextIO

from .commands import Command, commands


def main(argv: list[str], stdin: TextIO, stdout: TextIO) -> int:
    parser = ArgumentParser('mypy-baseline')
    subparsers = parser.add_subparsers()
    parser.set_defaults(cmd=None)

    cmd_class: type[Command]
    for name, cmd_class in sorted(commands.items()):
        subparser = subparsers.add_parser(name=name, help=cmd_class.__doc__)
        subparser.set_defaults(cmd=cmd_class)
        cmd_class.init_parser(subparser)
    args = parser.parse_args(argv)

    cmd_class = args.cmd
    if cmd_class is None:
        parser.print_help()
        return 1
    cmd = cmd_class(args=args, stdin=stdin, stdout=stdout)
    return cmd.run()


def entrypoint() -> NoReturn:
    sys.exit(main(argv=sys.argv[1:], stdin=sys.stdin, stdout=sys.stdout))

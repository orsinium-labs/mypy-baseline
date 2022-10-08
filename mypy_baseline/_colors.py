from __future__ import annotations

from dataclasses import dataclass
from typing import Any


RED = '\033[31m'
GREEN = '\033[32m'
BLUE = '\033[94m'
MAGENTA = '\033[35m'
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
    │ Great work! Please, run `mypy | mypy-baseline sync`
    │ to remove resolved violations from the baseline file.
    └────────────────────────────────────────────┄┄
"""


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

    def magenta(self, text: Any) -> str:
        if self.disabled:
            return str(text)
        return f'{MAGENTA}{text}{END}'

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

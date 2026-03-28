"""
BREAK command - break out of a loop.

Note: Module name is break_cmd.py because 'break' is a Python keyword.
"""

from ..process import Process
from ..command_decorators import command
from ..control_flow import BreakException
from . import register_command


@command()
@register_command('break')
def cmd_break(process: Process) -> int:
    """
    Break out of a loop

    Usage: break [n]

    Exit from the innermost enclosing loop, or from n enclosing loops.

    Arguments:
        n - Number of loops to break out of (default: 1)

    Examples:
        # Break from innermost loop
        for i in 1 2 3 4 5; do
            if test $i -eq 3; then
                break
            fi
            echo $i
        done
        # Output: 1, 2 (stops at 3)

        # Break from two nested loops
        for i in 1 2; do
            for j in a b c; do
                echo $i$j
                break 2
            done
        done
        # Output: 1a (breaks out of both loops)
    """
    levels = 1
    if process.args:
        try:
            levels = int(process.args[0])
            if levels < 1:
                levels = 1
        except ValueError:
            process.stderr.write(b"break: numeric argument required\n")
            return 1

    # Raise exception to be caught by executor
    raise BreakException(levels=levels)

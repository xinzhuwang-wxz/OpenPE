"""
CONTINUE command - continue to next iteration of a loop.

Note: Module name is continue_cmd.py because 'continue' is a Python keyword.
"""

from ..process import Process
from ..command_decorators import command
from ..control_flow import ContinueException
from . import register_command


@command()
@register_command('continue')
def cmd_continue(process: Process) -> int:
    """
    Continue to next iteration of a loop

    Usage: continue [n]

    Skip the rest of the current loop iteration and continue with the next one.
    If n is specified, continue the nth enclosing loop.

    Arguments:
        n - Which enclosing loop to continue (default: 1)

    Examples:
        # Continue innermost loop
        for i in 1 2 3 4 5; do
            if test $i -eq 3; then
                continue
            fi
            echo $i
        done
        # Output: 1, 2, 4, 5 (skips 3)

        # Continue outer loop (skip inner loop entirely)
        for i in 1 2; do
            for j in a b c; do
                if test "$j" = "b"; then
                    continue 2
                fi
                echo $i$j
            done
        done
        # Output: 1a, 2a (continues outer loop when j=b)
    """
    levels = 1
    if process.args:
        try:
            levels = int(process.args[0])
            if levels < 1:
                levels = 1
        except ValueError:
            process.stderr.write(b"continue: numeric argument required\n")
            return 1

    # Raise exception to be caught by executor
    raise ContinueException(levels=levels)

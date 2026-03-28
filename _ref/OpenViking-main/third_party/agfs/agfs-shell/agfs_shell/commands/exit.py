"""
EXIT command - exit the script with an optional exit code.
"""

import sys
from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('exit')
def cmd_exit(process: Process) -> int:
    """
    Exit the script with an optional exit code

    Usage: exit [n]

    Exit with status n (defaults to 0).
    In a script, exits the entire script.
    In interactive mode, exits the shell.

    Examples:
        exit        # Exit with status 0
        exit 1      # Exit with status 1
        exit $?     # Exit with last command's exit code
    """
    exit_code = 0
    if process.args:
        try:
            exit_code = int(process.args[0])
        except ValueError:
            process.stderr.write(f"exit: {process.args[0]}: numeric argument required\n")
            exit_code = 2

    # Exit by raising SystemExit
    sys.exit(exit_code)

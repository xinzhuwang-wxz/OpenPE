"""
FALSE command - return failure.
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('false')
def cmd_false(process: Process) -> int:
    """
    Return failure (exit code 1)

    Usage: false

    Always returns 1 (failure). Useful in scripts and conditionals.
    """
    return 1

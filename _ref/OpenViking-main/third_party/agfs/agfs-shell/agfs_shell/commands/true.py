"""
TRUE command - return success.
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('true')
def cmd_true(process: Process) -> int:
    """
    Return success (exit code 0)

    Usage: true

    Always returns 0 (success). Useful in scripts and conditionals.
    """
    return 0

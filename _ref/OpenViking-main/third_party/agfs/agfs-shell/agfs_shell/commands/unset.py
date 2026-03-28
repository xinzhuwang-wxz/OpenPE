"""
UNSET command - unset environment variables.
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('unset')
def cmd_unset(process: Process) -> int:
    """
    Unset environment variables

    Usage: unset VAR [VAR ...]
    """
    if not process.args:
        process.stderr.write("unset: missing variable name\n")
        return 1

    if not hasattr(process, 'env'):
        return 0

    for var_name in process.args:
        if var_name in process.env:
            del process.env[var_name]

    return 0

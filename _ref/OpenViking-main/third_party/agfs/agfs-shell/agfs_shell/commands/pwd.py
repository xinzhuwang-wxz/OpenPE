"""
PWD command - print working directory.
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('pwd')
def cmd_pwd(process: Process) -> int:
    """
    Print working directory

    Usage: pwd
    """
    # Get cwd from process metadata if available
    cwd = getattr(process, 'cwd', '/')
    process.stdout.write(f"{cwd}\n".encode('utf-8'))
    return 0

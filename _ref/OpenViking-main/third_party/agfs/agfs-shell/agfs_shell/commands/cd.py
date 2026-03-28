"""
CD command - change directory.
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command(no_pipeline=True, changes_cwd=True, needs_path_resolution=True)
@register_command('cd')
def cmd_cd(process: Process) -> int:
    """
    Change directory

    Usage: cd [path]

    Note: This is a special builtin that needs to be handled by the shell
    """
    if not process.args:
        # cd with no args goes to root
        target_path = '/'
    else:
        target_path = process.args[0]

    if not process.filesystem:
        process.stderr.write("cd: filesystem not available\n")
        return 1

    # Store the target path in process metadata for shell to handle
    # The shell will resolve the path and verify it exists
    process.cd_target = target_path

    # Return special exit code to indicate cd operation
    # Shell will check for this and update cwd
    return 0

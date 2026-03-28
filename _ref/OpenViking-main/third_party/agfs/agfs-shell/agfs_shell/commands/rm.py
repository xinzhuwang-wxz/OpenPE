"""
RM command - remove file or directory.
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command(needs_path_resolution=True)
@register_command('rm')
def cmd_rm(process: Process) -> int:
    """
    Remove file or directory

    Usage: rm [-r] path...
    """
    if not process.args:
        process.stderr.write("rm: missing operand\n")
        return 1

    if not process.filesystem:
        process.stderr.write("rm: filesystem not available\n")
        return 1

    recursive = False
    paths = []

    for arg in process.args:
        if arg == '-r' or arg == '-rf':
            recursive = True
        else:
            paths.append(arg)

    if not paths:
        process.stderr.write("rm: missing file operand\n")
        return 1

    exit_code = 0

    for path in paths:
        try:
            # Use AGFS client to remove file/directory
            process.filesystem.client.rm(path, recursive=recursive)
        except Exception as e:
            error_msg = str(e)
            process.stderr.write(f"rm: {path}: {error_msg}\n")
            exit_code = 1

    return exit_code

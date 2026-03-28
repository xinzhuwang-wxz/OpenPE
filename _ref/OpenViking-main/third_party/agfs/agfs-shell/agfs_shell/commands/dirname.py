"""
DIRNAME command - extract directory from path.
"""

import os
from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('dirname')
def cmd_dirname(process: Process) -> int:
    """
    Extract directory from path
    Usage: dirname PATH

    Examples:
        dirname /local/path/to/file.txt    # /local/path/to
        dirname /local/file.txt             # /local
        dirname file.txt                    # .
    """
    if not process.args:
        process.stderr.write("dirname: missing operand\n")
        process.stderr.write("Usage: dirname PATH\n")
        return 1

    path = process.args[0]

    # Extract dirname
    dirname = os.path.dirname(path)

    # If dirname is empty, use '.'
    if not dirname:
        dirname = '.'

    process.stdout.write(dirname + '\n')
    return 0

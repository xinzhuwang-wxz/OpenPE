"""
BASENAME command - extract filename from path.
"""

import os
from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('basename')
def cmd_basename(process: Process) -> int:
    """
    Extract filename from path
    Usage: basename PATH [SUFFIX]

    Examples:
        basename /local/path/to/file.txt         # file.txt
        basename /local/path/to/file.txt .txt    # file
    """
    if not process.args:
        process.stderr.write("basename: missing operand\n")
        process.stderr.write("Usage: basename PATH [SUFFIX]\n")
        return 1

    path = process.args[0]
    suffix = process.args[1] if len(process.args) > 1 else None

    # Extract basename
    basename = os.path.basename(path)

    # Remove suffix if provided
    if suffix and basename.endswith(suffix):
        basename = basename[:-len(suffix)]

    process.stdout.write(basename + '\n')
    return 0

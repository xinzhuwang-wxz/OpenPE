"""
SORT command - sort lines of text.
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('sort')
def cmd_sort(process: Process) -> int:
    """
    Sort lines of text

    Usage: sort [-r]
    """
    reverse = '-r' in process.args

    # Read lines from stdin
    lines = process.stdin.readlines()
    lines.sort(reverse=reverse)

    for line in lines:
        process.stdout.write(line)

    return 0

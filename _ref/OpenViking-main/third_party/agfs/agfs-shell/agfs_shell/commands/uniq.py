"""
UNIQ command - report or omit repeated lines.
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('uniq')
def cmd_uniq(process: Process) -> int:
    """
    Report or omit repeated lines

    Usage: uniq
    """
    lines = process.stdin.readlines()
    if not lines:
        return 0

    prev_line = lines[0]
    process.stdout.write(prev_line)

    for line in lines[1:]:
        if line != prev_line:
            process.stdout.write(line)
            prev_line = line

    return 0

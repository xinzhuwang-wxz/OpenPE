"""
HEAD command - output the first part of files.
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('head')
def cmd_head(process: Process) -> int:
    """
    Output the first part of files

    Usage: head [-n count]
    """
    n = 10  # default

    # Parse -n flag
    args = process.args[:]
    i = 0
    while i < len(args):
        if args[i] == '-n' and i + 1 < len(args):
            try:
                n = int(args[i + 1])
                i += 2
                continue
            except ValueError:
                process.stderr.write(f"head: invalid number: {args[i + 1]}\n")
                return 1
        i += 1

    # Read lines from stdin
    lines = process.stdin.readlines()
    for line in lines[:n]:
        process.stdout.write(line)

    return 0

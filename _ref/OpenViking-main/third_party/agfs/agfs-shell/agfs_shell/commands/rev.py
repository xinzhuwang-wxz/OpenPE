"""
REV command - reverse lines character-wise.
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('rev')
def cmd_rev(process: Process) -> int:
    """
    Reverse lines character-wise

    Usage: rev

    Examples:
        echo 'hello' | rev              # Output: olleh
        echo 'abc:def' | rev            # Output: fed:cba
        ls -l | rev | cut -d' ' -f1 | rev  # Extract filenames from ls -l
    """
    lines = process.stdin.readlines()

    for line in lines:
        # Handle both str and bytes
        if isinstance(line, bytes):
            line_str = line.decode('utf-8', errors='replace')
        else:
            line_str = line

        # Remove trailing newline, reverse, add newline back
        line_clean = line_str.rstrip('\n\r')
        reversed_line = line_clean[::-1]
        process.stdout.write(reversed_line + '\n')

    return 0

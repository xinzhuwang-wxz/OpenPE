"""
WC command - count lines, words, and bytes.
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('wc')
def cmd_wc(process: Process) -> int:
    """
    Count lines, words, and bytes

    Usage: wc [-l] [-w] [-c]
    """
    count_lines = False
    count_words = False
    count_bytes = False

    # Parse flags
    flags = [arg for arg in process.args if arg.startswith('-')]
    if not flags:
        # Default: count all
        count_lines = count_words = count_bytes = True
    else:
        for flag in flags:
            if 'l' in flag:
                count_lines = True
            if 'w' in flag:
                count_words = True
            if 'c' in flag:
                count_bytes = True

    # Read all data from stdin
    data = process.stdin.read()

    lines = data.count(b'\n')
    words = len(data.split())
    bytes_count = len(data)

    result = []
    if count_lines:
        result.append(str(lines))
    if count_words:
        result.append(str(words))
    if count_bytes:
        result.append(str(bytes_count))

    output = ' '.join(result) + '\n'
    process.stdout.write(output)

    return 0

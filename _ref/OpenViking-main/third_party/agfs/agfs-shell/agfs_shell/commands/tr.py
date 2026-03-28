"""
TR command - translate characters.
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('tr')
def cmd_tr(process: Process) -> int:
    """
    Translate characters

    Usage: tr set1 set2
    """
    if len(process.args) < 2:
        process.stderr.write("tr: missing operand\n")
        return 1

    set1 = process.args[0].encode('utf-8')
    set2 = process.args[1].encode('utf-8')

    if len(set1) != len(set2):
        process.stderr.write("tr: sets must be same length\n")
        return 1

    # Create translation table
    trans = bytes.maketrans(set1, set2)

    # Read and translate
    data = process.stdin.read()
    translated = data.translate(trans)
    process.stdout.write(translated)

    return 0

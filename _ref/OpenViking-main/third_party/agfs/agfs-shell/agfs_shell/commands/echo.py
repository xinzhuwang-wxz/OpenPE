"""
Echo command - print arguments to stdout.
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('echo')
def cmd_echo(process: Process) -> int:
    """Echo arguments to stdout"""
    if process.args:
        output = ' '.join(process.args) + '\n'
        process.stdout.write(output)
    else:
        process.stdout.write('\n')
    return 0

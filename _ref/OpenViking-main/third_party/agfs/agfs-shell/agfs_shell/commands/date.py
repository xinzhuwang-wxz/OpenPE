"""
DATE command - display or set the system date and time.
"""

import subprocess
from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('date')
def cmd_date(process: Process) -> int:
    """
    Display or set the system date and time by calling the system date command

    Usage: date [OPTION]... [+FORMAT]

    All arguments are passed directly to the system date command.
    """
    try:
        # Call the system date command with all provided arguments
        result = subprocess.run(
            ['date'] + process.args,
            capture_output=True,
            text=False  # Use bytes mode to preserve encoding
        )

        # Write stdout from date command to process stdout
        if result.stdout:
            process.stdout.write(result.stdout)

        # Write stderr from date command to process stderr
        if result.stderr:
            process.stderr.write(result.stderr)

        return result.returncode
    except FileNotFoundError:
        process.stderr.write(b"date: command not found\n")
        return 127
    except Exception as e:
        process.stderr.write(f"date: error: {str(e)}\n".encode('utf-8'))
        return 1

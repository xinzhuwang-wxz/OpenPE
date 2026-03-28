"""
SLEEP command - pause execution for specified seconds.
"""

import time
from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('sleep')
def cmd_sleep(process: Process) -> int:
    """
    Pause execution for specified seconds

    Usage: sleep SECONDS

    Examples:
        sleep 1      # Sleep for 1 second
        sleep 0.5    # Sleep for 0.5 seconds
        sleep 5      # Sleep for 5 seconds
    """
    if not process.args:
        process.stderr.write("sleep: missing operand\n")
        process.stderr.write("Usage: sleep SECONDS\n")
        return 1

    try:
        seconds = float(process.args[0])
        if seconds < 0:
            process.stderr.write("sleep: invalid time interval\n")
            return 1

        time.sleep(seconds)
        return 0
    except ValueError:
        process.stderr.write(f"sleep: invalid time interval '{process.args[0]}'\n")
        return 1
    except KeyboardInterrupt:
        # Re-raise KeyboardInterrupt to allow proper signal propagation
        # This allows the script executor to handle Ctrl-C properly
        raise

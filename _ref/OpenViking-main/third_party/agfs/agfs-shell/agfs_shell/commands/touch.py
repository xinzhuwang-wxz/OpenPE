"""
TOUCH command - touch file (update timestamp).
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command(needs_path_resolution=True)
@register_command('touch')
def cmd_touch(process: Process) -> int:
    """
    Touch file (update timestamp)

    Usage: touch file...
    """
    if not process.args:
        process.stderr.write("touch: missing file operand\n")
        return 1

    if not process.filesystem:
        process.stderr.write("touch: filesystem not available\n")
        return 1

    for path in process.args:
        try:
            process.filesystem.touch_file(path)
        except Exception as e:
            error_msg = str(e)
            process.stderr.write(f"touch: {path}: {error_msg}\n")
            return 1

    return 0

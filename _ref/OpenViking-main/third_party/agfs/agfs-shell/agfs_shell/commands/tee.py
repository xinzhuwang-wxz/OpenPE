"""
TEE command - read from stdin and write to both stdout and files.
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command(needs_path_resolution=True)
@register_command('tee')
def cmd_tee(process: Process) -> int:
    """
    Read from stdin and write to both stdout and files (streaming mode)

    Usage: tee [-a] [file...]

    Options:
        -a    Append to files instead of overwriting
    """
    append = False
    files = []

    # Parse arguments
    for arg in process.args:
        if arg == '-a':
            append = True
        else:
            files.append(arg)

    if files and not process.filesystem:
        process.stderr.write(b"tee: filesystem not available\n")
        return 1

    # Read input lines
    lines = process.stdin.readlines()

    # Write to stdout (streaming: flush after each line)
    for line in lines:
        process.stdout.write(line)
        process.stdout.flush()

    # Write to files
    if files:
        if append:
            # Append mode: must collect all data
            content = b''.join(lines)
            for filename in files:
                try:
                    process.filesystem.write_file(filename, content, append=True)
                except Exception as e:
                    process.stderr.write(f"tee: {filename}: {str(e)}\n".encode())
                    return 1
        else:
            # Non-append mode: use streaming write via iterator
            # Create an iterator from lines
            def line_iterator():
                for line in lines:
                    yield line

            for filename in files:
                try:
                    # Pass iterator to write_file for streaming
                    process.filesystem.write_file(filename, line_iterator(), append=False)
                except Exception as e:
                    process.stderr.write(f"tee: {filename}: {str(e)}\n".encode())
                    return 1

    return 0

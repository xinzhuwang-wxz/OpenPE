"""
LS command - list directory contents.
"""

import os
from ..process import Process
from ..command_decorators import command
from ..utils.formatters import mode_to_rwx, human_readable_size
from . import register_command


@command(needs_path_resolution=True)
@register_command('ls')
def cmd_ls(process: Process) -> int:
    """
    List directory contents

    Usage: ls [-l] [-h] [path...]

    Options:
        -l    Use long listing format
        -h    Print human-readable sizes (e.g., 1K, 234M, 2G)
    """
    # Parse arguments
    long_format = False
    human_readable_flag = False
    paths = []

    for arg in process.args:
        if arg.startswith('-') and arg != '-':
            # Handle combined flags like -lh
            if 'l' in arg:
                long_format = True
            if 'h' in arg:
                human_readable_flag = True
        else:
            paths.append(arg)

    # Default to current working directory if no paths specified
    if not paths:
        cwd = getattr(process, 'cwd', '/')
        paths = [cwd]

    if not process.filesystem:
        process.stderr.write("ls: filesystem not available\n")
        return 1

    # Helper function to format file info
    def format_file_info(file_info, display_name=None):
        """Format a single file info dict for output"""
        name = display_name if display_name else file_info.get('name', '')
        is_dir = file_info.get('isDir', False) or file_info.get('type') == 'directory'
        size = file_info.get('size', 0)

        if long_format:
            # Long format output similar to ls -l
            file_type = 'd' if is_dir else '-'

            # Get mode/permissions
            mode_str = file_info.get('mode', '')
            if mode_str and isinstance(mode_str, str) and len(mode_str) >= 9:
                # Already in rwxr-xr-x format
                perms = mode_str[:9]
            elif mode_str and isinstance(mode_str, int):
                # Convert octal mode to rwx format
                perms = mode_to_rwx(mode_str)
            else:
                # Default permissions
                perms = 'rwxr-xr-x' if is_dir else 'rw-r--r--'

            # Get modification time
            mtime = file_info.get('modTime', file_info.get('mtime', ''))
            if mtime:
                # Format timestamp (YYYY-MM-DD HH:MM:SS)
                if 'T' in mtime:
                    # ISO format: 2025-11-18T22:00:25Z
                    mtime = mtime.replace('T', ' ').replace('Z', '').split('.')[0]
                elif len(mtime) > 19:
                    # Truncate to 19 chars if too long
                    mtime = mtime[:19]
            else:
                mtime = '0000-00-00 00:00:00'

            # Format: permissions size date time name
            # Add color for directories (blue)
            if is_dir:
                # Blue color for directories
                colored_name = f"\033[1;34m{name}/\033[0m"
            else:
                colored_name = name

            # Format size based on human_readable flag
            if human_readable_flag:
                size_str = f"{human_readable_size(size):>8}"
            else:
                size_str = f"{size:>8}"

            return f"{file_type}{perms} {size_str} {mtime} {colored_name}\n"
        else:
            # Simple formatting
            if is_dir:
                # Blue color for directories
                return f"\033[1;34m{name}/\033[0m\n"
            else:
                return f"{name}\n"

    exit_code = 0

    try:
        # Process each path argument
        for path in paths:
            try:
                # First, get info about the path to determine if it's a file or directory
                path_info = process.filesystem.get_file_info(path)
                is_directory = path_info.get('isDir', False) or path_info.get('type') == 'directory'

                if is_directory:
                    # It's a directory - list its contents
                    files = process.filesystem.list_directory(path)

                    # Show directory name if multiple paths
                    if len(paths) > 1:
                        process.stdout.write(f"{path}:\n".encode('utf-8'))

                    for file_info in files:
                        output = format_file_info(file_info)
                        process.stdout.write(output.encode('utf-8'))

                    # Add blank line between directories if multiple paths
                    if len(paths) > 1:
                        process.stdout.write(b"\n")
                else:
                    # It's a file - display info about the file itself
                    basename = os.path.basename(path)
                    output = format_file_info(path_info, display_name=basename)
                    process.stdout.write(output.encode('utf-8'))

            except Exception as e:
                error_msg = str(e)
                if "No such file or directory" in error_msg or "not found" in error_msg.lower():
                    process.stderr.write(f"ls: {path}: No such file or directory\n")
                else:
                    process.stderr.write(f"ls: {path}: {error_msg}\n")
                exit_code = 1

        return exit_code
    except Exception as e:
        error_msg = str(e)
        process.stderr.write(f"ls: {error_msg}\n")
        return 1

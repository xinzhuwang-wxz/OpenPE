"""
TREE command - (auto-migrated from builtins.py)
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


def _print_tree(process, path, prefix, is_last, max_depth, current_depth, dirs_only, show_hidden, stats):
    """
    Recursively print directory tree

    Args:
        process: Process object
        path: Current directory path
        prefix: Prefix string for tree drawing
        is_last: Whether this is the last item in the parent directory
        max_depth: Maximum depth to traverse (None for unlimited)
        current_depth: Current depth level
        dirs_only: Only show directories
        show_hidden: Show hidden files
        stats: Dictionary to track file/dir counts
    """
    # Check depth limit
    if max_depth is not None and current_depth >= max_depth:
        return

    try:
        # List directory contents
        entries = process.filesystem.list_directory(path)

        # Filter entries
        filtered_entries = []
        for entry in entries:
            name = entry.get('name', '')

            # Skip hidden files unless show_hidden is True
            if not show_hidden and name.startswith('.'):
                continue

            is_dir = entry.get('isDir', False) or entry.get('type') == 'directory'

            # Skip files if dirs_only is True
            if dirs_only and not is_dir:
                continue

            filtered_entries.append(entry)

        # Sort entries: directories first, then by name
        filtered_entries.sort(key=lambda e: (not (e.get('isDir', False) or e.get('type') == 'directory'), e.get('name', '')))

        # Process each entry
        for idx, entry in enumerate(filtered_entries):
            name = entry.get('name', '')
            is_dir = entry.get('isDir', False) or entry.get('type') == 'directory'
            is_last_entry = (idx == len(filtered_entries) - 1)

            # Update statistics
            if is_dir:
                stats['dirs'] += 1
            else:
                stats['files'] += 1

            # Determine the tree characters to use
            if is_last_entry:
                connector = "└── "
                extension = "    "
            else:
                connector = "├── "
                extension = "│   "

            # Format name with color
            if is_dir:
                # Blue color for directories
                display_name = f"\033[1;34m{name}/\033[0m"
            else:
                display_name = name

            # Print the entry
            line = f"{prefix}{connector}{display_name}\n"
            process.stdout.write(line.encode('utf-8'))

            # Recursively process subdirectories
            if is_dir:
                subdir_path = os.path.join(path, name)
                subdir_path = os.path.normpath(subdir_path)
                new_prefix = prefix + extension

                _print_tree(
                    process,
                    subdir_path,
                    new_prefix,
                    is_last_entry,
                    max_depth,
                    current_depth + 1,
                    dirs_only,
                    show_hidden,
                    stats
                )

    except Exception as e:
        # If we can't read a directory, print an error but continue
        error_msg = str(e)
        if "Permission denied" in error_msg:
            error_line = f"{prefix}[error opening dir]\n"
        else:
            error_line = f"{prefix}[error: {error_msg}]\n"
        process.stdout.write(error_line.encode('utf-8'))



@command(needs_path_resolution=True, supports_streaming=True)
@register_command('tree')
def cmd_tree(process: Process) -> int:
    """
    List contents of directories in a tree-like format

    Usage: tree [OPTIONS] [path]

    Options:
        -L level    Descend only level directories deep
        -d          List directories only
        -a          Show all files (including hidden files starting with .)
        --noreport  Don't print file and directory count at the end

    Examples:
        tree                # Show tree of current directory
        tree /path/to/dir   # Show tree of specific directory
        tree -L 2           # Show tree with max depth of 2
        tree -d             # Show only directories
        tree -a             # Show all files including hidden ones
    """
    # Parse arguments
    max_depth = None
    dirs_only = False
    show_hidden = False
    show_report = True
    path = None

    args = process.args[:]
    i = 0
    while i < len(args):
        if args[i] == '-L' and i + 1 < len(args):
            try:
                max_depth = int(args[i + 1])
                if max_depth < 0:
                    process.stderr.write("tree: invalid level, must be >= 0\n")
                    return 1
                i += 2
                continue
            except ValueError:
                process.stderr.write(f"tree: invalid level '{args[i + 1]}'\n")
                return 1
        elif args[i] == '-d':
            dirs_only = True
            i += 1
        elif args[i] == '-a':
            show_hidden = True
            i += 1
        elif args[i] == '--noreport':
            show_report = False
            i += 1
        elif args[i].startswith('-'):
            # Handle combined flags
            if args[i] == '-L':
                process.stderr.write("tree: option requires an argument -- 'L'\n")
                return 1
            # Unknown option
            process.stderr.write(f"tree: invalid option -- '{args[i]}'\n")
            return 1
        else:
            # This is the path argument
            if path is not None:
                process.stderr.write("tree: too many arguments\n")
                return 1
            path = args[i]
            i += 1

    # Default to current working directory
    if path is None:
        path = getattr(process, 'cwd', '/')

    if not process.filesystem:
        process.stderr.write("tree: filesystem not available\n")
        return 1

    # Check if path exists
    try:
        info = process.filesystem.get_file_info(path)
        is_dir = info.get('isDir', False) or info.get('type') == 'directory'

        if not is_dir:
            process.stderr.write(f"tree: {path}: Not a directory\n")
            return 1
    except Exception as e:
        error_msg = str(e)
        if "No such file or directory" in error_msg or "not found" in error_msg.lower():
            process.stderr.write(f"tree: {path}: No such file or directory\n")
        else:
            process.stderr.write(f"tree: {path}: {error_msg}\n")
        return 1

    # Print the root path
    process.stdout.write(f"{path}\n".encode('utf-8'))

    # Track statistics
    stats = {'dirs': 0, 'files': 0}

    # Build and print the tree
    try:
        _print_tree(process, path, "", True, max_depth, 0, dirs_only, show_hidden, stats)
    except Exception as e:
        process.stderr.write(f"tree: error traversing {path}: {e}\n")
        return 1

    # Print report
    if show_report:
        if dirs_only:
            report = f"\n{stats['dirs']} directories\n"
        else:
            report = f"\n{stats['dirs']} directories, {stats['files']} files\n"
        process.stdout.write(report.encode('utf-8'))

    return 0


def _print_tree(process, path, prefix, is_last, max_depth, current_depth, dirs_only, show_hidden, stats):
    """
    Recursively print directory tree

    Args:
        process: Process object
        path: Current directory path
        prefix: Prefix string for tree drawing
        is_last: Whether this is the last item in the parent directory
        max_depth: Maximum depth to traverse (None for unlimited)
        current_depth: Current depth level
        dirs_only: Only show directories
        show_hidden: Show hidden files
        stats: Dictionary to track file/dir counts
    """
    # Check depth limit
    if max_depth is not None and current_depth >= max_depth:
        return

    try:
        # List directory contents
        entries = process.filesystem.list_directory(path)

        # Filter entries
        filtered_entries = []
        for entry in entries:
            name = entry.get('name', '')

            # Skip hidden files unless show_hidden is True
            if not show_hidden and name.startswith('.'):
                continue

            is_dir = entry.get('isDir', False) or entry.get('type') == 'directory'

            # Skip files if dirs_only is True
            if dirs_only and not is_dir:
                continue

            filtered_entries.append(entry)

        # Sort entries: directories first, then by name
        filtered_entries.sort(key=lambda e: (not (e.get('isDir', False) or e.get('type') == 'directory'), e.get('name', '')))

        # Process each entry
        for idx, entry in enumerate(filtered_entries):
            name = entry.get('name', '')
            is_dir = entry.get('isDir', False) or entry.get('type') == 'directory'
            is_last_entry = (idx == len(filtered_entries) - 1)

            # Update statistics
            if is_dir:
                stats['dirs'] += 1
            else:
                stats['files'] += 1

            # Determine the tree characters to use
            if is_last_entry:
                connector = "└── "
                extension = "    "
            else:
                connector = "├── "
                extension = "│   "

            # Format name with color
            if is_dir:
                # Blue color for directories
                display_name = f"\033[1;34m{name}/\033[0m"
            else:
                display_name = name

            # Print the entry
            line = f"{prefix}{connector}{display_name}\n"
            process.stdout.write(line.encode('utf-8'))

            # Recursively process subdirectories
            if is_dir:
                subdir_path = os.path.join(path, name)
                subdir_path = os.path.normpath(subdir_path)
                new_prefix = prefix + extension

                _print_tree(
                    process,
                    subdir_path,
                    new_prefix,
                    is_last_entry,
                    max_depth,
                    current_depth + 1,
                    dirs_only,
                    show_hidden,
                    stats
                )

    except Exception as e:
        # If we can't read a directory, print an error but continue
        error_msg = str(e)
        if "Permission denied" in error_msg:
            error_line = f"{prefix}[error opening dir]\n"
        else:
            error_line = f"{prefix}[error: {error_msg}]\n"
        process.stdout.write(error_line.encode('utf-8'))

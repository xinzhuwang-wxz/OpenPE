"""
DOWNLOAD command - (auto-migrated from builtins.py)
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('download')
def cmd_download(process: Process) -> int:
    """
    Download an AGFS file or directory to local filesystem

    Usage: download [-r] <agfs_path> <local_path>
    """
    # Parse arguments
    recursive = False
    args = process.args[:]

    if args and args[0] == '-r':
        recursive = True
        args = args[1:]

    if len(args) != 2:
        process.stderr.write("download: usage: download [-r] <agfs_path> <local_path>\n")
        return 1

    agfs_path = args[0]
    local_path = args[1]

    # Resolve agfs_path relative to current working directory
    if not agfs_path.startswith('/'):
        agfs_path = os.path.join(process.cwd, agfs_path)
        agfs_path = os.path.normpath(agfs_path)

    try:
        # Check if source path is a directory
        info = process.filesystem.get_file_info(agfs_path)

        # Check if destination is a local directory
        if os.path.isdir(local_path):
            # Destination is a directory, append source filename
            source_basename = os.path.basename(agfs_path)
            local_path = os.path.join(local_path, source_basename)

        if info.get('isDir', False):
            if not recursive:
                process.stderr.write(f"download: {agfs_path}: Is a directory (use -r to download recursively)\n")
                return 1
            # Download directory recursively
            return _download_dir(process, agfs_path, local_path)
        else:
            # Download single file
            return _download_file(process, agfs_path, local_path)

    except FileNotFoundError:
        process.stderr.write(f"download: {local_path}: Cannot create file\n")
        return 1
    except PermissionError:
        process.stderr.write(f"download: {local_path}: Permission denied\n")
        return 1
    except Exception as e:
        error_msg = str(e)
        if "No such file or directory" in error_msg or "not found" in error_msg.lower():
            process.stderr.write(f"download: {agfs_path}: No such file or directory\n")
        else:
            process.stderr.write(f"download: {error_msg}\n")
        return 1


def _download_file(process: Process, agfs_path: str, local_path: str, show_progress: bool = True) -> int:
    """Helper: Download a single file from AGFS"""
    try:
        stream = process.filesystem.read_file(agfs_path, stream=True)
        bytes_written = 0

        with open(local_path, 'wb') as f:
            for chunk in stream:
                if chunk:
                    f.write(chunk)
                    bytes_written += len(chunk)

        if show_progress:
            process.stdout.write(f"Downloaded {bytes_written} bytes to {local_path}\n")
            process.stdout.flush()
        return 0

    except Exception as e:
        process.stderr.write(f"download: {agfs_path}: {str(e)}\n")
        return 1


def _download_dir(process: Process, agfs_path: str, local_path: str) -> int:
    """Helper: Download a directory recursively from AGFS"""
    try:
        # Create local directory if it doesn't exist
        os.makedirs(local_path, exist_ok=True)

        # List AGFS directory
        entries = process.filesystem.list_directory(agfs_path)

        for entry in entries:
            name = entry['name']
            is_dir = entry.get('isDir', False)

            agfs_item = os.path.join(agfs_path, name)
            agfs_item = os.path.normpath(agfs_item)
            local_item = os.path.join(local_path, name)

            if is_dir:
                # Recursively download subdirectory
                result = _download_dir(process, agfs_item, local_item)
                if result != 0:
                    return result
            else:
                # Download file
                result = _download_file(process, agfs_item, local_item)
                if result != 0:
                    return result

        return 0

    except Exception as e:
        process.stderr.write(f"download: {str(e)}\n")
        return 1

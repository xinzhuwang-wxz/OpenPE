"""
CP command - copy files between local filesystem and AGFS.
"""

import os
from ..process import Process
from ..command_decorators import command
from . import register_command


def _upload_dir(process: Process, local_path: str, agfs_path: str) -> int:
    """Helper: Upload a directory recursively to AGFS"""
    import stat as stat_module

    try:
        # Create target directory in AGFS if it doesn't exist
        try:
            info = process.filesystem.get_file_info(agfs_path)
            if not info.get('isDir', False):
                process.stderr.write(f"upload: {agfs_path}: Not a directory\n")
                return 1
        except Exception:
            # Directory doesn't exist, create it
            try:
                # Use mkdir command to create directory
                from pyagfs import AGFSClient
                process.filesystem.client.mkdir(agfs_path)
            except Exception as e:
                process.stderr.write(f"upload: cannot create directory {agfs_path}: {str(e)}\n")
                return 1

        # Walk through local directory
        for root, dirs, files in os.walk(local_path):
            # Calculate relative path
            rel_path = os.path.relpath(root, local_path)
            if rel_path == '.':
                current_agfs_dir = agfs_path
            else:
                current_agfs_dir = os.path.join(agfs_path, rel_path)
                current_agfs_dir = os.path.normpath(current_agfs_dir)

            # Create subdirectories in AGFS
            for dirname in dirs:
                dir_agfs_path = os.path.join(current_agfs_dir, dirname)
                dir_agfs_path = os.path.normpath(dir_agfs_path)
                try:
                    process.filesystem.client.mkdir(dir_agfs_path)
                except Exception:
                    # Directory might already exist, ignore
                    pass

            # Upload files
            for filename in files:
                local_file = os.path.join(root, filename)
                agfs_file = os.path.join(current_agfs_dir, filename)
                agfs_file = os.path.normpath(agfs_file)

                result = _upload_file(process, local_file, agfs_file)
                if result != 0:
                    return result

        return 0

    except Exception as e:
        process.stderr.write(f"upload: {str(e)}\n")
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




def _cp_upload(process: Process, local_path: str, agfs_path: str, recursive: bool = False) -> int:
    """Helper: Upload local file or directory to AGFS

    Note: agfs_path should already be resolved to absolute path by caller
    """
    try:
        if not os.path.exists(local_path):
            process.stderr.write(f"cp: {local_path}: No such file or directory\n")
            return 1

        # Check if destination is a directory
        try:
            dest_info = process.filesystem.get_file_info(agfs_path)
            if dest_info.get('isDir', False):
                # Destination is a directory, append source filename
                source_basename = os.path.basename(local_path)
                agfs_path = os.path.join(agfs_path, source_basename)
                agfs_path = os.path.normpath(agfs_path)
        except Exception:
            # Destination doesn't exist, use as-is
            pass

        if os.path.isfile(local_path):
            # Show progress
            process.stdout.write(f"local:{local_path} -> {agfs_path}\n")
            process.stdout.flush()

            # Upload file
            with open(local_path, 'rb') as f:
                process.filesystem.write_file(agfs_path, f.read(), append=False)
            return 0

        elif os.path.isdir(local_path):
            if not recursive:
                process.stderr.write(f"cp: {local_path}: Is a directory (use -r to copy recursively)\n")
                return 1
            # Upload directory recursively
            return _upload_dir(process, local_path, agfs_path)

        else:
            process.stderr.write(f"cp: {local_path}: Not a file or directory\n")
            return 1

    except Exception as e:
        process.stderr.write(f"cp: {str(e)}\n")
        return 1


def _cp_download(process: Process, agfs_path: str, local_path: str, recursive: bool = False) -> int:
    """Helper: Download AGFS file or directory to local

    Note: agfs_path should already be resolved to absolute path by caller
    """
    try:
        # Check if source is a directory
        info = process.filesystem.get_file_info(agfs_path)

        # Check if destination is a local directory
        if os.path.isdir(local_path):
            # Destination is a directory, append source filename
            source_basename = os.path.basename(agfs_path)
            local_path = os.path.join(local_path, source_basename)

        if info.get('isDir', False):
            if not recursive:
                process.stderr.write(f"cp: {agfs_path}: Is a directory (use -r to copy recursively)\n")
                return 1
            # Download directory recursively
            return _download_dir(process, agfs_path, local_path)
        else:
            # Show progress
            process.stdout.write(f"{agfs_path} -> local:{local_path}\n")
            process.stdout.flush()

            # Download single file
            stream = process.filesystem.read_file(agfs_path, stream=True)
            with open(local_path, 'wb') as f:
                for chunk in stream:
                    if chunk:
                        f.write(chunk)
            return 0

    except FileNotFoundError:
        process.stderr.write(f"cp: {local_path}: Cannot create file\n")
        return 1
    except PermissionError:
        process.stderr.write(f"cp: {local_path}: Permission denied\n")
        return 1
    except Exception as e:
        error_msg = str(e)
        if "No such file or directory" in error_msg or "not found" in error_msg.lower():
            process.stderr.write(f"cp: {agfs_path}: No such file or directory\n")
        else:
            process.stderr.write(f"cp: {str(e)}\n")
        return 1


def _cp_agfs(process: Process, source_path: str, dest_path: str, recursive: bool = False) -> int:
    """Helper: Copy within AGFS

    Note: source_path and dest_path should already be resolved to absolute paths by caller
    """
    try:
        # Check if source is a directory
        info = process.filesystem.get_file_info(source_path)

        # Check if destination is a directory
        try:
            dest_info = process.filesystem.get_file_info(dest_path)
            if dest_info.get('isDir', False):
                # Destination is a directory, append source filename
                source_basename = os.path.basename(source_path)
                dest_path = os.path.join(dest_path, source_basename)
                dest_path = os.path.normpath(dest_path)
        except Exception:
            # Destination doesn't exist, use as-is
            pass

        if info.get('isDir', False):
            if not recursive:
                process.stderr.write(f"cp: {source_path}: Is a directory (use -r to copy recursively)\n")
                return 1
            # Copy directory recursively
            return _cp_agfs_dir(process, source_path, dest_path)
        else:
            # Show progress
            process.stdout.write(f"{source_path} -> {dest_path}\n")
            process.stdout.flush()

            # Copy single file - read all at once to avoid append overhead
            data = process.filesystem.read_file(source_path, stream=False)
            process.filesystem.write_file(dest_path, data, append=False)

            return 0

    except Exception as e:
        error_msg = str(e)
        if "No such file or directory" in error_msg or "not found" in error_msg.lower():
            process.stderr.write(f"cp: {source_path}: No such file or directory\n")
        else:
            process.stderr.write(f"cp: {str(e)}\n")
        return 1


def _cp_agfs_dir(process: Process, source_path: str, dest_path: str) -> int:
    """Helper: Recursively copy directory within AGFS"""
    try:
        # Create destination directory if it doesn't exist
        try:
            info = process.filesystem.get_file_info(dest_path)
            if not info.get('isDir', False):
                process.stderr.write(f"cp: {dest_path}: Not a directory\n")
                return 1
        except Exception:
            # Directory doesn't exist, create it
            try:
                process.filesystem.client.mkdir(dest_path)
            except Exception as e:
                process.stderr.write(f"cp: cannot create directory {dest_path}: {str(e)}\n")
                return 1

        # List source directory
        entries = process.filesystem.list_directory(source_path)

        for entry in entries:
            name = entry['name']
            is_dir = entry.get('isDir', False)

            src_item = os.path.join(source_path, name)
            src_item = os.path.normpath(src_item)
            dst_item = os.path.join(dest_path, name)
            dst_item = os.path.normpath(dst_item)

            if is_dir:
                # Recursively copy subdirectory
                result = _cp_agfs_dir(process, src_item, dst_item)
                if result != 0:
                    return result
            else:
                # Show progress
                process.stdout.write(f"{src_item} -> {dst_item}\n")
                process.stdout.flush()

                # Copy file - read all at once to avoid append overhead
                data = process.filesystem.read_file(src_item, stream=False)
                process.filesystem.write_file(dst_item, data, append=False)

        return 0

    except Exception as e:
        process.stderr.write(f"cp: {str(e)}\n")
        return 1



@command(needs_path_resolution=True)
@register_command('cp')
def cmd_cp(process: Process) -> int:
    """
    Copy files between local filesystem and AGFS

    Usage:
        cp [-r] <source>... <dest>
        cp [-r] local:<path> <agfs_path>   # Upload from local to AGFS
        cp [-r] <agfs_path> local:<path>   # Download from AGFS to local
        cp [-r] <agfs_path1> <agfs_path2>  # Copy within AGFS
    """
    import os

    # Parse arguments
    recursive = False
    args = process.args[:]

    if args and args[0] == '-r':
        recursive = True
        args = args[1:]

    if len(args) < 2:
        process.stderr.write("cp: usage: cp [-r] <source>... <dest>\n")
        return 1

    # Last argument is destination, all others are sources
    sources = args[:-1]
    dest = args[-1]

    # Parse dest to determine if it's local
    dest_is_local = dest.startswith('local:')
    if dest_is_local:
        dest = dest[6:]  # Remove 'local:' prefix
    else:
        # Resolve AGFS path relative to current working directory
        if not dest.startswith('/'):
            dest = os.path.join(process.cwd, dest)
            dest = os.path.normpath(dest)

    exit_code = 0

    # Process each source file
    for source in sources:
        # Parse source to determine operation type
        source_is_local = source.startswith('local:')

        if source_is_local:
            source = source[6:]  # Remove 'local:' prefix
        else:
            # Resolve AGFS path relative to current working directory
            if not source.startswith('/'):
                source = os.path.join(process.cwd, source)
                source = os.path.normpath(source)

        # Determine operation type
        if source_is_local and not dest_is_local:
            # Upload: local -> AGFS
            result = _cp_upload(process, source, dest, recursive)
        elif not source_is_local and dest_is_local:
            # Download: AGFS -> local
            result = _cp_download(process, source, dest, recursive)
        elif not source_is_local and not dest_is_local:
            # Copy within AGFS
            result = _cp_agfs(process, source, dest, recursive)
        else:
            # local -> local (not supported, use system cp)
            process.stderr.write("cp: local to local copy not supported, use system cp command\n")
            result = 1

        if result != 0:
            exit_code = result

    return exit_code


def _cp_upload(process: Process, local_path: str, agfs_path: str, recursive: bool = False) -> int:
    """Helper: Upload local file or directory to AGFS

    Note: agfs_path should already be resolved to absolute path by caller
    """
    try:
        if not os.path.exists(local_path):
            process.stderr.write(f"cp: {local_path}: No such file or directory\n")
            return 1

        # Check if destination is a directory
        try:
            dest_info = process.filesystem.get_file_info(agfs_path)
            if dest_info.get('isDir', False):
                # Destination is a directory, append source filename
                source_basename = os.path.basename(local_path)
                agfs_path = os.path.join(agfs_path, source_basename)
                agfs_path = os.path.normpath(agfs_path)
        except Exception:
            # Destination doesn't exist, use as-is
            pass

        if os.path.isfile(local_path):
            # Show progress
            process.stdout.write(f"local:{local_path} -> {agfs_path}\n")
            process.stdout.flush()

            # Upload file
            with open(local_path, 'rb') as f:
                process.filesystem.write_file(agfs_path, f.read(), append=False)
            return 0

        elif os.path.isdir(local_path):
            if not recursive:
                process.stderr.write(f"cp: {local_path}: Is a directory (use -r to copy recursively)\n")
                return 1
            # Upload directory recursively
            return _upload_dir(process, local_path, agfs_path)

        else:
            process.stderr.write(f"cp: {local_path}: Not a file or directory\n")
            return 1

    except Exception as e:
        process.stderr.write(f"cp: {str(e)}\n")
        return 1


def _cp_download(process: Process, agfs_path: str, local_path: str, recursive: bool = False) -> int:
    """Helper: Download AGFS file or directory to local

    Note: agfs_path should already be resolved to absolute path by caller
    """
    try:
        # Check if source is a directory
        info = process.filesystem.get_file_info(agfs_path)

        # Check if destination is a local directory
        if os.path.isdir(local_path):
            # Destination is a directory, append source filename
            source_basename = os.path.basename(agfs_path)
            local_path = os.path.join(local_path, source_basename)

        if info.get('isDir', False):
            if not recursive:
                process.stderr.write(f"cp: {agfs_path}: Is a directory (use -r to copy recursively)\n")
                return 1
            # Download directory recursively
            return _download_dir(process, agfs_path, local_path)
        else:
            # Show progress
            process.stdout.write(f"{agfs_path} -> local:{local_path}\n")
            process.stdout.flush()

            # Download single file
            stream = process.filesystem.read_file(agfs_path, stream=True)
            with open(local_path, 'wb') as f:
                for chunk in stream:
                    if chunk:
                        f.write(chunk)
            return 0

    except FileNotFoundError:
        process.stderr.write(f"cp: {local_path}: Cannot create file\n")
        return 1
    except PermissionError:
        process.stderr.write(f"cp: {local_path}: Permission denied\n")
        return 1
    except Exception as e:
        error_msg = str(e)
        if "No such file or directory" in error_msg or "not found" in error_msg.lower():
            process.stderr.write(f"cp: {agfs_path}: No such file or directory\n")
        else:
            process.stderr.write(f"cp: {str(e)}\n")
        return 1


def _cp_agfs(process: Process, source_path: str, dest_path: str, recursive: bool = False) -> int:
    """Helper: Copy within AGFS

    Note: source_path and dest_path should already be resolved to absolute paths by caller
    """
    try:
        # Check if source is a directory
        info = process.filesystem.get_file_info(source_path)

        # Check if destination is a directory
        try:
            dest_info = process.filesystem.get_file_info(dest_path)
            if dest_info.get('isDir', False):
                # Destination is a directory, append source filename
                source_basename = os.path.basename(source_path)
                dest_path = os.path.join(dest_path, source_basename)
                dest_path = os.path.normpath(dest_path)
        except Exception:
            # Destination doesn't exist, use as-is
            pass

        if info.get('isDir', False):
            if not recursive:
                process.stderr.write(f"cp: {source_path}: Is a directory (use -r to copy recursively)\n")
                return 1
            # Copy directory recursively
            return _cp_agfs_dir(process, source_path, dest_path)
        else:
            # Show progress
            process.stdout.write(f"{source_path} -> {dest_path}\n")
            process.stdout.flush()

            # Copy single file - read all at once to avoid append overhead
            data = process.filesystem.read_file(source_path, stream=False)
            process.filesystem.write_file(dest_path, data, append=False)

            return 0

    except Exception as e:
        error_msg = str(e)
        if "No such file or directory" in error_msg or "not found" in error_msg.lower():
            process.stderr.write(f"cp: {source_path}: No such file or directory\n")
        else:
            process.stderr.write(f"cp: {str(e)}\n")
        return 1


def _cp_agfs_dir(process: Process, source_path: str, dest_path: str) -> int:
    """Helper: Recursively copy directory within AGFS"""
    try:
        # Create destination directory if it doesn't exist
        try:
            info = process.filesystem.get_file_info(dest_path)
            if not info.get('isDir', False):
                process.stderr.write(f"cp: {dest_path}: Not a directory\n")
                return 1
        except Exception:
            # Directory doesn't exist, create it
            try:
                process.filesystem.client.mkdir(dest_path)
            except Exception as e:
                process.stderr.write(f"cp: cannot create directory {dest_path}: {str(e)}\n")
                return 1

        # List source directory
        entries = process.filesystem.list_directory(source_path)

        for entry in entries:
            name = entry['name']
            is_dir = entry.get('isDir', False)

            src_item = os.path.join(source_path, name)
            src_item = os.path.normpath(src_item)
            dst_item = os.path.join(dest_path, name)
            dst_item = os.path.normpath(dst_item)

            if is_dir:
                # Recursively copy subdirectory
                result = _cp_agfs_dir(process, src_item, dst_item)
                if result != 0:
                    return result
            else:
                # Show progress
                process.stdout.write(f"{src_item} -> {dst_item}\n")
                process.stdout.flush()

                # Copy file - read all at once to avoid append overhead
                data = process.filesystem.read_file(src_item, stream=False)
                process.filesystem.write_file(dst_item, data, append=False)

        return 0

    except Exception as e:
        process.stderr.write(f"cp: {str(e)}\n")
        return 1



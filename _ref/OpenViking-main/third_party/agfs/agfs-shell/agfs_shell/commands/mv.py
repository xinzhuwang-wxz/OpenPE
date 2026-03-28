"""
MV command - (auto-migrated from builtins.py)
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command(needs_path_resolution=True)
@register_command('mv')
def cmd_mv(process: Process) -> int:
    """
    Move (rename) files and directories

    Usage: mv [OPTIONS] SOURCE DEST
           mv [OPTIONS] SOURCE... DIRECTORY

    Options:
        -i          Prompt before overwrite (interactive mode)
        -n          Do not overwrite an existing file
        -f          Force overwrite without prompting (default)

    Path formats:
        <agfs_path>      - AGFS path (default)
        local:<path>     - Local filesystem path

    Examples:
        mv file.txt newname.txt                    # Rename within AGFS
        mv file1.txt file2.txt dir/                # Move multiple files to directory
        mv local:file.txt /agfs/path/              # Move from local to AGFS
        mv /agfs/file.txt local:~/Downloads/       # Move from AGFS to local
        mv -i file.txt existing.txt                # Prompt before overwriting
        mv -n file.txt existing.txt                # Don't overwrite if exists
    """
    # Parse options
    interactive = False
    no_clobber = False
    force = True  # Default behavior
    args = process.args[:]
    sources = []

    i = 0
    while i < len(args):
        if args[i] == '-i':
            interactive = True
            force = False
            i += 1
        elif args[i] == '-n':
            no_clobber = True
            force = False
            i += 1
        elif args[i] == '-f':
            force = True
            interactive = False
            no_clobber = False
            i += 1
        elif args[i].startswith('-'):
            # Handle combined flags like -in
            for char in args[i][1:]:
                if char == 'i':
                    interactive = True
                    force = False
                elif char == 'n':
                    no_clobber = True
                    force = False
                elif char == 'f':
                    force = True
                    interactive = False
                    no_clobber = False
                else:
                    process.stderr.write(f"mv: invalid option -- '{char}'\n")
                    return 1
            i += 1
        else:
            sources.append(args[i])
            i += 1

    # Need at least source and dest
    if len(sources) < 2:
        process.stderr.write("mv: missing file operand\n")
        process.stderr.write("Usage: mv [OPTIONS] SOURCE DEST\n")
        process.stderr.write("       mv [OPTIONS] SOURCE... DIRECTORY\n")
        return 1

    dest = sources.pop()

    # Parse source and dest to determine if local or AGFS
    source_paths = []
    for src in sources:
        is_local = src.startswith('local:')
        path = src[6:] if is_local else src
        source_paths.append({'path': path, 'is_local': is_local, 'original': src})

    dest_is_local = dest.startswith('local:')
    dest_path = dest[6:] if dest_is_local else dest

    # Resolve AGFS paths relative to cwd
    if not dest_is_local and not dest_path.startswith('/'):
        dest_path = os.path.join(process.cwd, dest_path)
        dest_path = os.path.normpath(dest_path)

    for src_info in source_paths:
        if not src_info['is_local'] and not src_info['path'].startswith('/'):
            src_info['path'] = os.path.join(process.cwd, src_info['path'])
            src_info['path'] = os.path.normpath(src_info['path'])

    # Check if moving multiple files
    if len(source_paths) > 1:
        # Multiple sources - dest must be a directory
        if dest_is_local:
            if not os.path.isdir(dest_path):
                process.stderr.write(f"mv: target '{dest}' is not a directory\n")
                return 1
        else:
            try:
                dest_info = process.filesystem.get_file_info(dest_path)
                if not (dest_info.get('isDir', False) or dest_info.get('type') == 'directory'):
                    process.stderr.write(f"mv: target '{dest}' is not a directory\n")
                    return 1
            except:
                process.stderr.write(f"mv: target '{dest}' is not a directory\n")
                return 1

        # Move each source to dest directory
        for src_info in source_paths:
            result = _mv_single(
                process, src_info['path'], dest_path,
                src_info['is_local'], dest_is_local,
                interactive, no_clobber, force,
                src_info['original'], dest
            )
            if result != 0:
                return result
    else:
        # Single source
        src_info = source_paths[0]
        return _mv_single(
            process, src_info['path'], dest_path,
            src_info['is_local'], dest_is_local,
            interactive, no_clobber, force,
            src_info['original'], dest
        )

    return 0


def _mv_single(process, source_path, dest_path, source_is_local, dest_is_local,
               interactive, no_clobber, force, source_display, dest_display):
    """
    Move a single file or directory

    Returns 0 on success, non-zero on failure
    """
    import sys

    # Determine final destination path
    final_dest = dest_path

    # Check if destination exists and is a directory
    dest_exists = False
    dest_is_dir = False

    if dest_is_local:
        dest_exists = os.path.exists(dest_path)
        dest_is_dir = os.path.isdir(dest_path)
    else:
        try:
            dest_info = process.filesystem.get_file_info(dest_path)
            dest_exists = True
            dest_is_dir = dest_info.get('isDir', False) or dest_info.get('type') == 'directory'
        except:
            dest_exists = False
            dest_is_dir = False

    # If dest is a directory, append source filename
    if dest_exists and dest_is_dir:
        source_basename = os.path.basename(source_path)
        if dest_is_local:
            final_dest = os.path.join(dest_path, source_basename)
        else:
            final_dest = os.path.join(dest_path, source_basename)
            final_dest = os.path.normpath(final_dest)

    # Check if final destination exists
    final_dest_exists = False
    if dest_is_local:
        final_dest_exists = os.path.exists(final_dest)
    else:
        try:
            process.filesystem.get_file_info(final_dest)
            final_dest_exists = True
        except:
            final_dest_exists = False

    # Handle overwrite protection
    if final_dest_exists:
        if no_clobber:
            # Don't overwrite, silently skip
            return 0

        if interactive:
            # Prompt user
            process.stderr.write(f"mv: overwrite '{final_dest}'? (y/n) ")
            process.stderr.flush()
            try:
                response = sys.stdin.readline().strip().lower()
                if response not in ['y', 'yes']:
                    return 0
            except:
                return 0

    # Perform the move operation based on source and dest types
    try:
        if source_is_local and dest_is_local:
            # Local to local - use os.rename or shutil.move
            import shutil
            shutil.move(source_path, final_dest)
            return 0

        elif source_is_local and not dest_is_local:
            # Local to AGFS - upload then delete local
            if os.path.isdir(source_path):
                # Move directory
                result = _upload_dir(process, source_path, final_dest)
                if result == 0:
                    # Delete local directory after successful upload
                    import shutil
                    shutil.rmtree(source_path)
                return result
            else:
                # Move file
                with open(source_path, 'rb') as f:
                    data = f.read()
                    process.filesystem.write_file(final_dest, data, append=False)
                # Delete local file after successful upload
                os.remove(source_path)
                return 0

        elif not source_is_local and dest_is_local:
            # AGFS to local - download then delete AGFS
            source_info = process.filesystem.get_file_info(source_path)
            is_dir = source_info.get('isDir', False) or source_info.get('type') == 'directory'

            if is_dir:
                # Move directory
                result = _download_dir(process, source_path, final_dest)
                if result == 0:
                    # Delete AGFS directory after successful download
                    process.filesystem.client.rm(source_path, recursive=True)
                return result
            else:
                # Move file
                stream = process.filesystem.read_file(source_path, stream=True)
                with open(final_dest, 'wb') as f:
                    for chunk in stream:
                        if chunk:
                            f.write(chunk)
                # Delete AGFS file after successful download
                process.filesystem.client.rm(source_path, recursive=False)
                return 0

        else:
            # AGFS to AGFS - use rename if supported, otherwise copy + delete
            # Check if source exists
            source_info = process.filesystem.get_file_info(source_path)

            # Try to use AGFS rename/move if available
            if hasattr(process.filesystem.client, 'rename'):
                process.filesystem.client.rename(source_path, final_dest)
            elif hasattr(process.filesystem.client, 'mv'):
                process.filesystem.client.mv(source_path, final_dest)
            else:
                # Fallback: copy then delete
                is_dir = source_info.get('isDir', False) or source_info.get('type') == 'directory'

                if is_dir:
                    # Copy directory recursively
                    result = _cp_agfs_dir(process, source_path, final_dest)
                    if result != 0:
                        return result
                    # Delete source directory
                    process.filesystem.client.rm(source_path, recursive=True)
                else:
                    # Copy file
                    data = process.filesystem.read_file(source_path, stream=False)
                    process.filesystem.write_file(final_dest, data, append=False)
                    # Delete source file
                    process.filesystem.client.rm(source_path, recursive=False)

            return 0

    except FileNotFoundError:
        process.stderr.write(f"mv: cannot stat '{source_display}': No such file or directory\n")
        return 1
    except PermissionError:
        process.stderr.write(f"mv: cannot move '{source_display}': Permission denied\n")
        return 1
    except Exception as e:
        error_msg = str(e)
        if "No such file or directory" in error_msg or "not found" in error_msg.lower():
            process.stderr.write(f"mv: cannot stat '{source_display}': No such file or directory\n")
        else:
            process.stderr.write(f"mv: cannot move '{source_display}' to '{dest_display}': {error_msg}\n")
        return 1

"""
GREP command - search for patterns in files.
"""

import re
from io import StringIO
from ..process import Process
from ..command_decorators import command
from . import register_command


def _grep_search(process, regex, filename, invert_match, show_line_numbers,
                 count_only, files_only, show_filename, file_obj=None):
    """
    Helper function to search for pattern in a file or stdin

    Returns True if any matches found, False otherwise
    """
    if file_obj is None:
        # Read from stdin
        lines = process.stdin.readlines()
    else:
        # Read from file object
        lines = file_obj.readlines()

    match_count = 0
    line_number = 0

    for line in lines:
        line_number += 1

        # Handle both str and bytes
        if isinstance(line, bytes):
            line_str = line.decode('utf-8', errors='replace')
        else:
            line_str = line

        # Remove trailing newline for matching
        line_clean = line_str.rstrip('\n\r')

        # Check if line matches
        matches = bool(regex.search(line_clean))
        if invert_match:
            matches = not matches

        if matches:
            match_count += 1

            if files_only:
                # Just print filename and stop processing this file
                if filename:
                    process.stdout.write(f"{filename}\n")
                return True

            if not count_only:
                # Build output line
                output_parts = []

                if show_filename and filename:
                    output_parts.append(filename)

                if show_line_numbers:
                    output_parts.append(str(line_number))

                # Format: filename:linenum:line or just line
                if output_parts:
                    prefix = ':'.join(output_parts) + ':'
                    process.stdout.write(prefix + line_clean + '\n')
                else:
                    process.stdout.write(line_str if line_str.endswith('\n') else line_clean + '\n')

    # If count_only, print the count
    if count_only:
        if show_filename and filename:
            process.stdout.write(f"{filename}:{match_count}\n")
        else:
            process.stdout.write(f"{match_count}\n")

    return match_count > 0


@command(supports_streaming=True)
@register_command('grep')
def cmd_grep(process: Process) -> int:
    """
    Search for pattern in files or stdin

    Usage: grep [OPTIONS] PATTERN [FILE...]

    Options:
        -i          Ignore case
        -v          Invert match (select non-matching lines)
        -n          Print line numbers
        -c          Count matching lines
        -l          Print only filenames with matches
        -h          Suppress filename prefix (default for single file)
        -H          Print filename prefix (default for multiple files)

    Examples:
        echo 'hello world' | grep hello
        grep 'pattern' file.txt
        grep -i 'error' *.log
        grep -n 'function' code.py
        grep -v 'debug' app.log
        grep -c 'TODO' *.py
    """
    # Parse options
    ignore_case = False
    invert_match = False
    show_line_numbers = False
    count_only = False
    files_only = False
    show_filename = None  # None = auto, True = force, False = suppress

    args = process.args[:]
    options = []

    while args and args[0].startswith('-') and args[0] != '-':
        opt = args.pop(0)
        if opt == '--':
            break

        for char in opt[1:]:
            if char == 'i':
                ignore_case = True
            elif char == 'v':
                invert_match = True
            elif char == 'n':
                show_line_numbers = True
            elif char == 'c':
                count_only = True
            elif char == 'l':
                files_only = True
            elif char == 'h':
                show_filename = False
            elif char == 'H':
                show_filename = True
            else:
                process.stderr.write(f"grep: invalid option -- '{char}'\n")
                return 2

    # Get pattern
    if not args:
        process.stderr.write("grep: missing pattern\n")
        process.stderr.write("Usage: grep [OPTIONS] PATTERN [FILE...]\n")
        return 2

    pattern = args.pop(0)
    files = args

    # Compile regex
    try:
        flags = re.IGNORECASE if ignore_case else 0
        regex = re.compile(pattern, flags)
    except re.error as e:
        process.stderr.write(f"grep: invalid pattern: {e}\n")
        return 2

    # Determine if we should show filenames
    if show_filename is None:
        show_filename = len(files) > 1

    # Process files or stdin
    total_matched = False

    if not files:
        # Read from stdin
        total_matched = _grep_search(
            process, regex, None, invert_match, show_line_numbers,
            count_only, files_only, False
        )
    else:
        # Read from files
        for filepath in files:
            try:
                # Read file content
                content = process.filesystem.read_file(filepath)
                if isinstance(content, bytes):
                    content = content.decode('utf-8')

                # Create a file-like object for the content
                file_obj = StringIO(content)

                matched = _grep_search(
                    process, regex, filepath, invert_match, show_line_numbers,
                    count_only, files_only, show_filename, file_obj
                )

                if matched:
                    total_matched = True
                    if files_only:
                        # Already printed filename, move to next file
                        continue

            except FileNotFoundError:
                process.stderr.write(f"grep: {filepath}: No such file or directory\n")
            except Exception as e:
                process.stderr.write(f"grep: {filepath}: {e}\n")

    return 0 if total_matched else 1

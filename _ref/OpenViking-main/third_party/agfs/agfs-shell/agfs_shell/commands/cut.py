"""
CUT command - cut out selected portions of each line.
"""

from typing import List
from ..process import Process
from ..command_decorators import command
from . import register_command


def _parse_cut_list(list_str: str) -> List:
    """
    Parse a cut list specification (e.g., "1,3,5-7,10-")
    Returns a list of (start, end) tuples representing ranges (1-indexed)
    """
    ranges = []

    for part in list_str.split(','):
        part = part.strip()

        if '-' in part and not part.startswith('-'):
            # Range like "5-7" or "5-"
            parts = part.split('-', 1)
            start_str = parts[0].strip()
            end_str = parts[1].strip() if parts[1] else None

            if not start_str:
                raise ValueError(f"invalid range: {part}")

            start = int(start_str)
            end = int(end_str) if end_str else None

            if start < 1:
                raise ValueError(f"fields and positions are numbered from 1")

            if end is not None and end < start:
                raise ValueError(f"invalid range: {part}")

            ranges.append((start, end))

        elif part.startswith('-'):
            # Range like "-5" (from 1 to 5)
            end_str = part[1:].strip()
            if not end_str:
                raise ValueError(f"invalid range: {part}")

            end = int(end_str)
            if end < 1:
                raise ValueError(f"fields and positions are numbered from 1")

            ranges.append((1, end))

        else:
            # Single number like "3"
            num = int(part)
            if num < 1:
                raise ValueError(f"fields and positions are numbered from 1")

            ranges.append((num, num))

    return ranges


def _cut_fields(process: Process, field_ranges: List, delimiter: str) -> int:
    """
    Cut fields from input lines based on field ranges
    """
    lines = process.stdin.readlines()

    for line in lines:
        # Handle both str and bytes
        if isinstance(line, bytes):
            line_str = line.decode('utf-8', errors='replace').rstrip('\n\r')
        else:
            line_str = line.rstrip('\n\r')

        # Split line by delimiter
        fields = line_str.split(delimiter)

        # Extract selected fields
        output_fields = []
        for start, end in field_ranges:
            if end is None:
                # Range like "3-" (from 3 to end)
                for i in range(start - 1, len(fields)):
                    if i < len(fields) and fields[i] not in output_fields:
                        output_fields.append((i, fields[i]))
            else:
                # Range like "3-5" or single field "3"
                for i in range(start - 1, end):
                    if i < len(fields) and fields[i] not in [f[1] for f in output_fields if f[0] == i]:
                        output_fields.append((i, fields[i]))

        # Sort by original field index to maintain order
        output_fields.sort(key=lambda x: x[0])

        # Output the selected fields
        if output_fields:
            output = delimiter.join([f[1] for f in output_fields]) + '\n'
            process.stdout.write(output)

    return 0


def _cut_chars(process: Process, char_ranges: List) -> int:
    """
    Cut characters from input lines based on character ranges
    """
    lines = process.stdin.readlines()

    for line in lines:
        # Handle both str and bytes
        if isinstance(line, bytes):
            line_str = line.decode('utf-8', errors='replace').rstrip('\n\r')
        else:
            line_str = line.rstrip('\n\r')

        # Extract selected characters
        output_chars = []
        for start, end in char_ranges:
            if end is None:
                # Range like "3-" (from 3 to end)
                for i in range(start - 1, len(line_str)):
                    if i < len(line_str):
                        output_chars.append((i, line_str[i]))
            else:
                # Range like "3-5" or single character "3"
                for i in range(start - 1, end):
                    if i < len(line_str):
                        output_chars.append((i, line_str[i]))

        # Sort by original character index to maintain order
        output_chars.sort(key=lambda x: x[0])

        # Remove duplicates while preserving order
        seen = set()
        unique_chars = []
        for idx, char in output_chars:
            if idx not in seen:
                seen.add(idx)
                unique_chars.append(char)

        # Output the selected characters
        if unique_chars:
            output = ''.join(unique_chars) + '\n'
            process.stdout.write(output)

    return 0


@command()
@register_command('cut')
def cmd_cut(process: Process) -> int:
    """
    Cut out selected portions of each line

    Usage: cut [OPTIONS]

    Options:
        -f LIST     Select only these fields (comma-separated or range)
        -d DELIM    Use DELIM as field delimiter (default: TAB)
        -c LIST     Select only these characters (comma-separated or range)

    LIST can be:
        N       N'th field/character, counted from 1
        N-M     From N'th to M'th (inclusive)
        N-      From N'th to end of line
        -M      From first to M'th (inclusive)

    Examples:
        echo 'a:b:c:d' | cut -d: -f1        # Output: a
        echo 'a:b:c:d' | cut -d: -f2-3      # Output: b:c
        echo 'a:b:c:d' | cut -d: -f1,3      # Output: a:c
        echo 'hello world' | cut -c1-5      # Output: hello
        cat /etc/passwd | cut -d: -f1,3     # Get username and UID
    """
    # Parse options
    fields_str = None
    delimiter = '\t'
    chars_str = None

    args = process.args[:]

    i = 0
    while i < len(args):
        if args[i] == '-f' and i + 1 < len(args):
            fields_str = args[i + 1]
            i += 2
        elif args[i] == '-d' and i + 1 < len(args):
            delimiter = args[i + 1]
            i += 2
        elif args[i] == '-c' and i + 1 < len(args):
            chars_str = args[i + 1]
            i += 2
        elif args[i].startswith('-f'):
            # Handle -f1 format
            fields_str = args[i][2:]
            i += 1
        elif args[i].startswith('-d'):
            # Handle -d: format
            delimiter = args[i][2:]
            i += 1
        elif args[i].startswith('-c'):
            # Handle -c1-5 format
            chars_str = args[i][2:]
            i += 1
        else:
            process.stderr.write(f"cut: invalid option -- '{args[i]}'\n")
            return 1

    # Check that either -f or -c is specified (but not both)
    if fields_str and chars_str:
        process.stderr.write("cut: only one type of list may be specified\n")
        return 1

    if not fields_str and not chars_str:
        process.stderr.write("cut: you must specify a list of bytes, characters, or fields\n")
        process.stderr.write("Usage: cut -f LIST [-d DELIM] or cut -c LIST\n")
        return 1

    try:
        if fields_str:
            # Parse field list
            field_indices = _parse_cut_list(fields_str)
            return _cut_fields(process, field_indices, delimiter)
        else:
            # Parse character list
            char_indices = _parse_cut_list(chars_str)
            return _cut_chars(process, char_indices)

    except ValueError as e:
        process.stderr.write(f"cut: {e}\n")
        return 1

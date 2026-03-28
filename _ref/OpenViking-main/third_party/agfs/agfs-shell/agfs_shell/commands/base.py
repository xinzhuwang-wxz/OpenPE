"""
Base utilities for command implementations.

This module provides common helper functions that command modules can use
to reduce code duplication and maintain consistency.
"""

from typing import List, Optional
from ..process import Process


def write_error(process: Process, message: str, prefix_command: bool = True):
    """
    Write an error message to stderr.

    Args:
        process: The process object
        message: The error message
        prefix_command: If True, prefix message with command name
    """
    if prefix_command:
        process.stderr.write(f"{process.command}: {message}\n")
    else:
        process.stderr.write(f"{message}\n")


def validate_arg_count(process: Process, min_args: int = 0, max_args: Optional[int] = None,
                       usage: str = "") -> bool:
    """
    Validate the number of arguments.

    Args:
        process: The process object
        min_args: Minimum required arguments
        max_args: Maximum allowed arguments (None = unlimited)
        usage: Usage string to display on error

    Returns:
        True if valid, False if invalid (error already written to stderr)
    """
    arg_count = len(process.args)

    if arg_count < min_args:
        write_error(process, f"missing operand")
        if usage:
            process.stderr.write(f"usage: {usage}\n")
        return False

    if max_args is not None and arg_count > max_args:
        write_error(process, f"too many arguments")
        if usage:
            process.stderr.write(f"usage: {usage}\n")
        return False

    return True


def parse_flags_and_args(args: List[str], known_flags: Optional[set] = None) -> tuple:
    """
    Parse command arguments into flags and positional arguments.

    Args:
        args: List of arguments
        known_flags: Set of known flag names (e.g., {'-r', '-h', '-a'})
                    If None, all args starting with '-' are treated as flags

    Returns:
        Tuple of (flags_dict, positional_args)
        flags_dict maps flag name to True (e.g., {'-r': True})
        positional_args is list of non-flag arguments
    """
    flags = {}
    positional = []
    i = 0

    while i < len(args):
        arg = args[i]

        # Check for '--' which stops flag parsing
        if arg == '--':
            # All remaining args are positional
            positional.extend(args[i + 1:])
            break

        # Check if it looks like a flag
        if arg.startswith('-') and len(arg) > 1:
            if known_flags is None or arg in known_flags:
                flags[arg] = True
                i += 1
            else:
                # Unknown flag, treat as positional
                positional.append(arg)
                i += 1
        else:
            # Positional argument
            positional.append(arg)
            i += 1

    return flags, positional


def has_flag(flags: dict, *flag_names: str) -> bool:
    """
    Check if any of the given flags are present.

    Args:
        flags: Dictionary of flags (from parse_flags_and_args)
        *flag_names: One or more flag names to check

    Returns:
        True if any of the flags are present

    Example:
        >>> flags = {'-r': True, '-v': True}
        >>> has_flag(flags, '-r')
        True
        >>> has_flag(flags, '-a')
        False
        >>> has_flag(flags, '-r', '--recursive')
        True
    """
    return any(name in flags for name in flag_names)


__all__ = [
    'write_error',
    'validate_arg_count',
    'parse_flags_and_args',
    'has_flag',
]

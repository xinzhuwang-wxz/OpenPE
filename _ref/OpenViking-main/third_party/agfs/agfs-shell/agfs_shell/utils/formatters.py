"""
Formatting utilities for agfs-shell commands.

This module provides common formatting functions used across multiple commands.
"""


def mode_to_rwx(mode: int) -> str:
    """
    Convert octal file mode to rwx string format.

    Args:
        mode: File mode as integer (e.g., 0o100644 or 420 decimal)

    Returns:
        String representation like 'rw-r--r--'

    Example:
        >>> mode_to_rwx(0o644)
        'rw-r--r--'
        >>> mode_to_rwx(0o755)
        'rwxr-xr-x'
    """
    # Handle both full mode (e.g., 0o100644) and just permissions (e.g., 0o644 or 420 decimal)
    # Extract last 9 bits for user/group/other permissions
    perms = mode & 0o777

    def _triple(val):
        """Convert 3-bit value to rwx"""
        r = 'r' if val & 4 else '-'
        w = 'w' if val & 2 else '-'
        x = 'x' if val & 1 else '-'
        return r + w + x

    # Split into user, group, other (3 bits each)
    user = (perms >> 6) & 7
    group = (perms >> 3) & 7
    other = perms & 7

    return _triple(user) + _triple(group) + _triple(other)


def human_readable_size(size: int) -> str:
    """
    Convert size in bytes to human-readable format.

    Args:
        size: Size in bytes

    Returns:
        Human-readable string like '1.5K', '2.3M', '100B'

    Example:
        >>> human_readable_size(1024)
        '1K'
        >>> human_readable_size(1536)
        '1.5K'
        >>> human_readable_size(1048576)
        '1M'
    """
    units = ['B', 'K', 'M', 'G', 'T', 'P']
    unit_index = 0
    size_float = float(size)

    while size_float >= 1024.0 and unit_index < len(units) - 1:
        size_float /= 1024.0
        unit_index += 1

    if unit_index == 0:
        # Bytes - no decimal
        return f"{int(size_float)}{units[unit_index]}"
    elif size_float >= 10:
        # >= 10 - no decimal places
        return f"{int(size_float)}{units[unit_index]}"
    else:
        # < 10 - one decimal place
        return f"{size_float:.1f}{units[unit_index]}"


__all__ = ['mode_to_rwx', 'human_readable_size']

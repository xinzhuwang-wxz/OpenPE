"""
Unified argument parsing for built-in commands

Provides consistent argument parsing to avoid duplication in builtins.py
"""

from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass


@dataclass
class ParsedArgs:
    """
    Result of argument parsing

    Attributes:
        positional: Positional arguments (non-flags)
        flags: Set of boolean flags (e.g., '-l', '-r')
        options: Dictionary of options with values (e.g., {'-n': '10'})
        remaining: Unparsed arguments after '--'
    """
    positional: List[str]
    flags: Set[str]
    options: Dict[str, str]
    remaining: List[str]

    def has_flag(self, *flags: str) -> bool:
        """Check if any of the given flags is present"""
        for flag in flags:
            if flag in self.flags:
                return True
        return False

    def get_option(self, *names: str, default: Optional[str] = None) -> Optional[str]:
        """Get value of first matching option"""
        for name in names:
            if name in self.options:
                return self.options[name]
        return default

    def get_int_option(self, *names: str, default: int = 0) -> int:
        """Get integer value of option"""
        value = self.get_option(*names)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default


class StandardArgParser:
    """
    Standard argument parser for built-in commands

    Handles common patterns:
    - Boolean flags: -l, -r, -h, etc.
    - Options with values: -n 10, --count=5
    - Combined flags: -lh (same as -l -h)
    - End of options: -- (everything after is positional)
    """

    def __init__(self, known_flags: Optional[Set[str]] = None,
                 known_options: Optional[Set[str]] = None):
        """
        Initialize parser

        Args:
            known_flags: Set of recognized boolean flags (e.g., {'-l', '-r'})
            known_options: Set of options that take values (e.g., {'-n', '--count'})
        """
        self.known_flags = known_flags or set()
        self.known_options = known_options or set()

    def parse(self, args: List[str]) -> ParsedArgs:
        """
        Parse argument list

        Args:
            args: List of command arguments

        Returns:
            ParsedArgs object with parsed arguments
        """
        positional = []
        flags = set()
        options = {}
        remaining = []

        i = 0
        end_of_options = False

        while i < len(args):
            arg = args[i]

            # Check for end-of-options marker
            if arg == '--':
                end_of_options = True
                remaining = args[i+1:]
                break

            # After --, everything is positional
            if end_of_options:
                positional.append(arg)
                i += 1
                continue

            # Check for options and flags
            if arg.startswith('-') and len(arg) > 1:
                # Long option with value: --name=value
                if arg.startswith('--') and '=' in arg:
                    name, value = arg.split('=', 1)
                    options[name] = value
                    i += 1
                # Long option requiring next arg: --count 10
                elif arg.startswith('--') and arg in self.known_options:
                    if i + 1 < len(args):
                        options[arg] = args[i + 1]
                        i += 2
                    else:
                        # Option without value - treat as flag
                        flags.add(arg)
                        i += 1
                # Short option requiring next arg: -n 10
                elif arg in self.known_options:
                    if i + 1 < len(args):
                        options[arg] = args[i + 1]
                        i += 2
                    else:
                        # Option without value - treat as flag
                        flags.add(arg)
                        i += 1
                # Combined short flags: -lh or individual flag -l
                else:
                    # Try to split combined flags
                    if not arg.startswith('--'):
                        for char in arg[1:]:
                            flags.add(f'-{char}')
                    else:
                        flags.add(arg)
                    i += 1
            else:
                # Positional argument
                positional.append(arg)
                i += 1

        return ParsedArgs(
            positional=positional,
            flags=flags,
            options=options,
            remaining=remaining
        )


def parse_standard_flags(args: List[str], valid_flags: str = '') -> Tuple[Set[str], List[str]]:
    """
    Simple flag parser for common cases

    Args:
        args: Argument list
        valid_flags: String of valid flag characters (e.g., 'lhr' for -l, -h, -r)

    Returns:
        Tuple of (flags_set, remaining_args)

    Example:
        >>> flags, args = parse_standard_flags(['-lh', 'file.txt'], 'lhr')
        >>> flags
        {'-l', '-h'}
        >>> args
        ['file.txt']
    """
    flags = set()
    remaining = []

    for arg in args:
        if arg.startswith('-') and len(arg) > 1 and arg != '--':
            # Extract flags from argument like -lh
            for char in arg[1:]:
                if char in valid_flags:
                    flags.add(f'-{char}')
        else:
            remaining.append(arg)

    return flags, remaining


def has_any_flag(args: List[str], *flag_chars: str) -> bool:
    """
    Quick check if any flag is present

    Args:
        args: Argument list
        *flag_chars: Flag characters to check (without '-')

    Returns:
        True if any flag is present

    Example:
        >>> has_any_flag(['-l', 'file.txt'], 'l', 'h')
        True
        >>> has_any_flag(['file.txt'], 'l', 'h')
        False
    """
    for arg in args:
        if arg.startswith('-') and len(arg) > 1:
            for char in flag_chars:
                if char in arg[1:]:
                    return True
    return False


def extract_option_value(args: List[str], *option_names: str, default: Optional[str] = None) -> Tuple[Optional[str], List[str]]:
    """
    Extract option value and return remaining args

    Args:
        args: Argument list
        *option_names: Option names to look for (e.g., '-n', '--count')
        default: Default value if option not found

    Returns:
        Tuple of (option_value, remaining_args)

    Example:
        >>> value, remaining = extract_option_value(['-n', '10', 'file.txt'], '-n', '--count')
        >>> value
        '10'
        >>> remaining
        ['file.txt']
    """
    remaining = []
    value = default
    i = 0

    while i < len(args):
        arg = args[i]

        # Check for option=value format
        if '=' in arg:
            for opt in option_names:
                if arg.startswith(f'{opt}='):
                    value = arg.split('=', 1)[1]
                    i += 1
                    continue

        # Check for option value format
        matched = False
        for opt in option_names:
            if arg == opt:
                if i + 1 < len(args):
                    value = args[i + 1]
                    i += 2
                    matched = True
                    break
                else:
                    i += 1
                    matched = True
                    break

        if not matched:
            remaining.append(arg)
            i += 1

    return value, remaining


class CommandArgumentValidator:
    """Validate command arguments based on rules"""

    @staticmethod
    def require_args(args: List[str], min_count: int = 1, error_msg: str = None) -> bool:
        """
        Check if minimum number of arguments is present

        Args:
            args: Argument list
            min_count: Minimum required arguments
            error_msg: Custom error message

        Returns:
            True if valid, raises ValueError otherwise

        Raises:
            ValueError: If not enough arguments
        """
        if len(args) < min_count:
            msg = error_msg or f"missing operand (expected at least {min_count} argument(s))"
            raise ValueError(msg)
        return True

    @staticmethod
    def require_exact_args(args: List[str], count: int, error_msg: str = None) -> bool:
        """Check if exact number of arguments is present"""
        if len(args) != count:
            msg = error_msg or f"expected exactly {count} argument(s), got {len(args)}"
            raise ValueError(msg)
        return True

    @staticmethod
    def validate_int(value: str, arg_name: str = "value") -> int:
        """Validate and convert string to integer"""
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"invalid integer value for {arg_name}: {value}")

    @staticmethod
    def validate_positive_int(value: str, arg_name: str = "value") -> int:
        """Validate positive integer"""
        num = CommandArgumentValidator.validate_int(value, arg_name)
        if num < 0:
            raise ValueError(f"{arg_name} must be positive: {value}")
        return num

"""
Command registry for agfs-shell builtin commands.

This module provides the command registration and discovery mechanism.
Each command is implemented in a separate module file under this directory.
"""

from typing import Dict, Callable, Optional
from ..process import Process

# Global command registry
_COMMANDS: Dict[str, Callable[[Process], int]] = {}


def register_command(*names: str):
    """
    Decorator to register a command function.

    Args:
        *names: One or more command names (for aliases like 'test' and '[')

    Example:
        @register_command('echo')
        def cmd_echo(process: Process) -> int:
            ...

        @register_command('test', '[')
        def cmd_test(process: Process) -> int:
            ...
    """
    def decorator(func: Callable[[Process], int]):
        for name in names:
            _COMMANDS[name] = func
        return func
    return decorator


def get_builtin(command: str) -> Optional[Callable[[Process], int]]:
    """
    Get a built-in command executor by name.

    Args:
        command: The command name to look up

    Returns:
        The command function, or None if not found
    """
    return _COMMANDS.get(command)


def load_all_commands():
    """
    Import all command modules to populate the registry.

    This function imports all command modules from this package,
    which causes their @register_command decorators to execute
    and populate the _COMMANDS registry.
    """
    # Import all command modules here
    # Each import will execute the @register_command decorator
    # and add the command to the registry

    # This will be populated as we migrate commands
    # For now, we'll import them dynamically
    import importlib
    import pkgutil
    import os

    # Get the directory containing this __init__.py
    package_dir = os.path.dirname(__file__)

    # Iterate through all .py files in the commands directory
    for _, module_name, _ in pkgutil.iter_modules([package_dir]):
        if module_name != 'base':  # Skip base.py as it's not a command
            try:
                importlib.import_module(f'.{module_name}', package=__name__)
            except Exception as e:
                # Log but don't fail if a command module has issues
                import sys
                print(f"Warning: Failed to load command module {module_name}: {e}", file=sys.stderr)


# Backward compatibility: BUILTINS dictionary
# This allows old code to use BUILTINS dict while we migrate
BUILTINS = _COMMANDS


__all__ = ['register_command', 'get_builtin', 'load_all_commands', 'BUILTINS']

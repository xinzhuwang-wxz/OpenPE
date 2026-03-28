"""
HELP command - display help information for built-in commands.
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('help', '?')
def cmd_help(process: Process) -> int:
    """
    Display help information for built-in commands

    Usage: ? [command]
           help [command]

    Without arguments: List all available commands
    With command name: Show detailed help for that command

    Examples:
        ?                # List all commands
        ? ls             # Show help for ls command
        help grep        # Show help for grep command
    """
    from . import _COMMANDS as BUILTINS

    if not process.args:
        # Show all commands
        process.stdout.write("Available built-in commands:\n\n")

        # Get all commands from BUILTINS, sorted alphabetically
        # Exclude '[' as it's an alias for 'test'
        commands = sorted([cmd for cmd in BUILTINS.keys() if cmd != '['])

        # Group commands by category for better organization
        categories = {
            'File Operations': ['ls', 'tree', 'cat', 'mkdir', 'rm', 'mv', 'cp', 'stat', 'upload', 'download'],
            'Text Processing': ['grep', 'wc', 'head', 'tail', 'sort', 'uniq', 'tr', 'rev', 'cut', 'jq', 'tee'],
            'System': ['pwd', 'cd', 'echo', 'env', 'export', 'unset', 'sleep', 'basename', 'dirname', 'date'],
            'Testing': ['test'],
            'AGFS Management': ['mount', 'plugins'],
            'Control Flow': ['break', 'continue', 'exit', 'return', 'local'],
        }

        # Display categorized commands
        for category, cmd_list in categories.items():
            category_cmds = [cmd for cmd in cmd_list if cmd in commands]
            if category_cmds:
                process.stdout.write(f"\033[1;36m{category}:\033[0m\n")
                for cmd in category_cmds:
                    func = BUILTINS[cmd]
                    # Get first line of docstring as short description
                    if func.__doc__:
                        lines = func.__doc__.strip().split('\n')
                        # Find first non-empty line after initial whitespace
                        short_desc = ""
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('Usage:'):
                                short_desc = line
                                break
                        process.stdout.write(f"  \033[1;32m{cmd:12}\033[0m {short_desc}\n")
                    else:
                        process.stdout.write(f"  \033[1;32m{cmd:12}\033[0m\n")
                process.stdout.write("\n")

        # Show uncategorized commands if any
        categorized = set()
        for cmd_list in categories.values():
            categorized.update(cmd_list)
        uncategorized = [cmd for cmd in commands if cmd not in categorized]
        if uncategorized:
            process.stdout.write(f"\033[1;36mOther:\033[0m\n")
            for cmd in uncategorized:
                func = BUILTINS[cmd]
                if func.__doc__:
                    lines = func.__doc__.strip().split('\n')
                    short_desc = ""
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('Usage:'):
                            short_desc = line
                            break
                    process.stdout.write(f"  \033[1;32m{cmd:12}\033[0m {short_desc}\n")
                else:
                    process.stdout.write(f"  \033[1;32m{cmd:12}\033[0m\n")
            process.stdout.write("\n")

        process.stdout.write("Type '? <command>' for detailed help on a specific command.\n")
        return 0

    # Show help for specific command
    command_name = process.args[0]

    if command_name not in BUILTINS:
        process.stderr.write(f"?: unknown command '{command_name}'\n")
        process.stderr.write("Type '?' to see all available commands.\n")
        return 1

    func = BUILTINS[command_name]

    if not func.__doc__:
        process.stdout.write(f"No help available for '{command_name}'\n")
        return 0

    # Display the full docstring
    process.stdout.write(f"\033[1;36mCommand: {command_name}\033[0m\n\n")

    # Format the docstring nicely
    docstring = func.__doc__.strip()

    # Process the docstring to add colors
    lines = docstring.split('\n')
    for line in lines:
        stripped = line.strip()

        # Highlight section headers (Usage:, Options:, Examples:, etc.)
        if stripped.endswith(':') and len(stripped.split()) == 1:
            process.stdout.write(f"\033[1;33m{stripped}\033[0m\n")
        # Highlight option flags
        elif stripped.startswith('-'):
            # Split option and description
            parts = stripped.split(None, 1)
            if len(parts) == 2:
                option, desc = parts
                process.stdout.write(f"  \033[1;32m{option:12}\033[0m {desc}\n")
            else:
                process.stdout.write(f"  \033[1;32m{stripped}\033[0m\n")
        # Regular line
        else:
            process.stdout.write(f"{line}\n")

    process.stdout.write("\n")
    return 0

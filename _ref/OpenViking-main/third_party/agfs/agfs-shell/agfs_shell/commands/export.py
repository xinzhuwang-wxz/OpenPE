"""
EXPORT command - set or display environment variables.
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('export')
def cmd_export(process: Process) -> int:
    """
    Set or display environment variables

    Usage: export [VAR=value ...]
    """
    if not process.args:
        # Display all environment variables (like 'env')
        if hasattr(process, 'env'):
            for key, value in sorted(process.env.items()):
                process.stdout.write(f"{key}={value}\n".encode('utf-8'))
        return 0

    # Set environment variables
    for arg in process.args:
        if '=' in arg:
            var_name, var_value = arg.split('=', 1)
            var_name = var_name.strip()
            var_value = var_value.strip()

            # Validate variable name
            if var_name and var_name.replace('_', '').replace('-', '').isalnum():
                if hasattr(process, 'env'):
                    process.env[var_name] = var_value
            else:
                process.stderr.write(f"export: invalid variable name: {var_name}\n")
                return 1
        else:
            process.stderr.write(f"export: usage: export VAR=value\n")
            return 1

    return 0

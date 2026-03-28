"""
LOCAL command - declare local variables (only valid within functions).
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command()
@register_command('local')
def cmd_local(process: Process) -> int:
    """
    Declare local variables (only valid within functions)

    Usage: local VAR=value [VAR2=value2 ...]

    Examples:
        local name="Alice"
        local count=0
        local path=/tmp/data
    """
    # Check if we have any local scopes (we're inside a function)
    # Note: This check needs to be done via env since we don't have direct access to shell
    # We'll use a special marker in env to track function depth
    if not process.env.get('_function_depth'):
        process.stderr.write("local: can only be used in a function\n")
        return 1

    if not process.args:
        process.stderr.write("local: usage: local VAR=value [VAR2=value2 ...]\n")
        return 2

    # Process each variable assignment
    for arg in process.args:
        if '=' not in arg:
            process.stderr.write(f"local: {arg}: not a valid identifier\n")
            return 1

        parts = arg.split('=', 1)
        var_name = parts[0].strip()
        var_value = parts[1] if len(parts) > 1 else ''

        # Validate variable name
        if not var_name or not var_name.replace('_', '').isalnum():
            process.stderr.write(f"local: {var_name}: not a valid identifier\n")
            return 1

        # Remove outer quotes if present
        if len(var_value) >= 2:
            if (var_value[0] == '"' and var_value[-1] == '"') or \
               (var_value[0] == "'" and var_value[-1] == "'"):
                var_value = var_value[1:-1]

        # Mark this variable as local by using a special prefix in env
        # This is a workaround since we don't have direct access to shell.local_scopes
        process.env[f'_local_{var_name}'] = var_value

    return 0

"""
TEST command - evaluate conditional expressions.
"""

from typing import List
from ..process import Process
from ..command_decorators import command
from . import register_command


def _evaluate_test_expression(args: List[str], process: Process) -> bool:
    """Evaluate a test expression"""
    if not args:
        return False

    # Single argument - test if non-empty string
    if len(args) == 1:
        return bool(args[0])

    # Negation operator
    if args[0] == '!':
        return not _evaluate_test_expression(args[1:], process)

    # File test operators
    if args[0] == '-f':
        if len(args) < 2:
            raise ValueError("-f requires an argument")
        path = args[1]
        if process.filesystem:
            try:
                info = process.filesystem.get_file_info(path)
                is_dir = info.get('isDir', False) or info.get('type') == 'directory'
                return not is_dir
            except:
                return False
        return False

    if args[0] == '-d':
        if len(args) < 2:
            raise ValueError("-d requires an argument")
        path = args[1]
        if process.filesystem:
            return process.filesystem.is_directory(path)
        return False

    if args[0] == '-e':
        if len(args) < 2:
            raise ValueError("-e requires an argument")
        path = args[1]
        if process.filesystem:
            return process.filesystem.file_exists(path)
        return False

    # String test operators
    if args[0] == '-z':
        if len(args) < 2:
            raise ValueError("-z requires an argument")
        return len(args[1]) == 0

    if args[0] == '-n':
        if len(args) < 2:
            raise ValueError("-n requires an argument")
        return len(args[1]) > 0

    # Binary operators
    if len(args) >= 3:
        # Logical AND
        if '-a' in args:
            idx = args.index('-a')
            left = _evaluate_test_expression(args[:idx], process)
            right = _evaluate_test_expression(args[idx+1:], process)
            return left and right

        # Logical OR
        if '-o' in args:
            idx = args.index('-o')
            left = _evaluate_test_expression(args[:idx], process)
            right = _evaluate_test_expression(args[idx+1:], process)
            return left or right

        # String comparison
        if args[1] == '=':
            return args[0] == args[2]

        if args[1] == '!=':
            return args[0] != args[2]

        # Integer comparison
        if args[1] in ['-eq', '-ne', '-gt', '-lt', '-ge', '-le']:
            try:
                left = int(args[0])
                right = int(args[2])
                if args[1] == '-eq':
                    return left == right
                elif args[1] == '-ne':
                    return left != right
                elif args[1] == '-gt':
                    return left > right
                elif args[1] == '-lt':
                    return left < right
                elif args[1] == '-ge':
                    return left >= right
                elif args[1] == '-le':
                    return left <= right
            except ValueError:
                raise ValueError(f"integer expression expected: {args[0]} or {args[2]}")

    # Default: non-empty first argument
    return bool(args[0])


@command()
@register_command('test', '[')
def cmd_test(process: Process) -> int:
    """
    Evaluate conditional expressions (similar to bash test/[)

    Usage: test EXPRESSION
           [ EXPRESSION ]

    File operators:
      -f FILE    True if file exists and is a regular file
      -d FILE    True if file exists and is a directory
      -e FILE    True if file exists

    String operators:
      -z STRING  True if string is empty
      -n STRING  True if string is not empty
      STRING1 = STRING2   True if strings are equal
      STRING1 != STRING2  True if strings are not equal

    Integer operators:
      INT1 -eq INT2  True if integers are equal
      INT1 -ne INT2  True if integers are not equal
      INT1 -gt INT2  True if INT1 is greater than INT2
      INT1 -lt INT2  True if INT1 is less than INT2
      INT1 -ge INT2  True if INT1 is greater than or equal to INT2
      INT1 -le INT2  True if INT1 is less than or equal to INT2

    Logical operators:
      ! EXPR     True if expr is false
      EXPR -a EXPR  True if both expressions are true (AND)
      EXPR -o EXPR  True if either expression is true (OR)
    """
    # Handle [ command - last arg should be ]
    if process.command == '[':
        if not process.args or process.args[-1] != ']':
            process.stderr.write("[: missing ']'\n")
            return 2
        # Remove the closing ]
        process.args = process.args[:-1]

    if not process.args:
        # Empty test is false
        return 1

    # Evaluate the expression
    try:
        result = _evaluate_test_expression(process.args, process)
        return 0 if result else 1
    except Exception as e:
        process.stderr.write(f"test: {e}\n")
        return 2

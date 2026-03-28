"""
JQ command - process JSON using jq-like syntax.
"""

from ..process import Process
from ..command_decorators import command
from . import register_command


@command(supports_streaming=True)
@register_command('jq')
def cmd_jq(process: Process) -> int:
    """
    Process JSON using jq-like syntax

    Usage:
        jq FILTER [file...]
        cat file.json | jq FILTER

    Examples:
        echo '{"name":"test"}' | jq .
        cat data.json | jq '.name'
        jq '.items[]' data.json
    """
    try:
        import jq as jq_lib
        import json
    except ImportError:
        process.stderr.write("jq: jq library not installed (run: uv pip install jq)\n")
        return 1

    # First argument is the filter
    if not process.args:
        process.stderr.write("jq: missing filter expression\n")
        process.stderr.write("Usage: jq FILTER [file...]\n")
        return 1

    filter_expr = process.args[0]
    input_files = process.args[1:] if len(process.args) > 1 else []

    try:
        # Compile the jq filter
        compiled_filter = jq_lib.compile(filter_expr)
    except Exception as e:
        process.stderr.write(f"jq: compile error: {e}\n")
        return 1

    # Read JSON input
    json_data = []

    if input_files:
        # Read from files
        for filepath in input_files:
            try:
                # Read file content
                content = process.filesystem.read_file(filepath)
                if isinstance(content, bytes):
                    content = content.decode('utf-8')

                # Parse JSON
                data = json.loads(content)
                json_data.append(data)
            except FileNotFoundError:
                process.stderr.write(f"jq: {filepath}: No such file or directory\n")
                return 1
            except json.JSONDecodeError as e:
                process.stderr.write(f"jq: {filepath}: parse error: {e}\n")
                return 1
            except Exception as e:
                process.stderr.write(f"jq: {filepath}: {e}\n")
                return 1
    else:
        # Read from stdin
        stdin_data = process.stdin.read()
        if isinstance(stdin_data, bytes):
            stdin_data = stdin_data.decode('utf-8')

        if not stdin_data.strip():
            process.stderr.write("jq: no input\n")
            return 1

        try:
            data = json.loads(stdin_data)
            json_data.append(data)
        except json.JSONDecodeError as e:
            process.stderr.write(f"jq: parse error: {e}\n")
            return 1

    # Apply filter to each JSON input
    try:
        for data in json_data:
            # Run the filter
            results = compiled_filter.input(data)

            # Output results
            for result in results:
                # Pretty print JSON output
                output = json.dumps(result, indent=2, ensure_ascii=False)
                process.stdout.write(output + '\n')

        return 0
    except Exception as e:
        process.stderr.write(f"jq: filter error: {e}\n")
        return 1

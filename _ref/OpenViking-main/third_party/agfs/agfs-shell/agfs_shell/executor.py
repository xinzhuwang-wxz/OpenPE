"""
AST Executor for shell control flow structures.

This module executes AST nodes and handles control flow properly
using Python exceptions for break/continue/return.
"""

from typing import List, TYPE_CHECKING
from .ast_nodes import (
    Statement, CommandStatement,
    ForStatement, WhileStatement, UntilStatement,
    IfStatement, FunctionDefinition
)
from .control_flow import (
    BreakException, ContinueException, ReturnException
)

if TYPE_CHECKING:
    from .shell import Shell


class ShellExecutor:
    """
    Executes AST nodes in the context of a Shell instance.

    This class handles proper control flow propagation using exceptions.
    """

    def __init__(self, shell: 'Shell'):
        """
        Initialize executor.

        Args:
            shell: Shell instance for command execution and variable access
        """
        self.shell = shell
        self.loop_depth = 0  # Current loop nesting depth
        self.function_depth = 0  # Current function nesting depth

    # ========================================================================
    # Main Entry Point
    # ========================================================================

    def execute_statement(self, stmt: Statement) -> int:
        """
        Execute a single statement.

        Args:
            stmt: Statement AST node

        Returns:
            Exit code of the statement
        """
        if isinstance(stmt, CommandStatement):
            return self.execute_command(stmt)
        elif isinstance(stmt, ForStatement):
            return self.execute_for(stmt)
        elif isinstance(stmt, WhileStatement):
            return self.execute_while(stmt)
        elif isinstance(stmt, UntilStatement):
            return self.execute_until(stmt)
        elif isinstance(stmt, IfStatement):
            return self.execute_if(stmt)
        elif isinstance(stmt, FunctionDefinition):
            return self.execute_function_def(stmt)
        else:
            # Unknown statement type
            return 0

    def execute_block(self, statements: List[Statement]) -> int:
        """
        Execute a block of statements.

        Break/Continue/Return exceptions propagate through.

        Args:
            statements: List of Statement AST nodes

        Returns:
            Exit code of last executed statement
        """
        last_exit_code = 0

        for stmt in statements:
            last_exit_code = self.execute_statement(stmt)

        return last_exit_code

    # ========================================================================
    # Statement Executors
    # ========================================================================

    def execute_command(self, stmt: CommandStatement) -> int:
        """
        Execute a simple command.

        This delegates to shell.execute() for actual command execution.
        """
        return self.shell.execute(stmt.command)

    def execute_for(self, stmt: ForStatement) -> int:
        """
        Execute a for loop.

        Example:
            for i in 1 2 3; do echo $i; done
        """
        # Expand items (variable expansion, glob expansion)
        items_str = self.shell._expand_variables(stmt.items_raw)
        items = items_str.split()

        # Expand globs
        expanded_items = []
        for item in items:
            if '*' in item or '?' in item or '[' in item:
                matches = self.shell._match_glob_pattern(item)
                if matches:
                    expanded_items.extend(sorted(matches))
                else:
                    expanded_items.append(item)
            else:
                expanded_items.append(item)

        last_exit_code = 0
        self.loop_depth += 1

        try:
            for item in expanded_items:
                # Set loop variable
                self.shell.env[stmt.variable] = item

                try:
                    last_exit_code = self.execute_block(stmt.body)
                except ContinueException as e:
                    if e.levels <= 1:
                        # Continue to next iteration
                        continue
                    else:
                        # Propagate to outer loop
                        e.levels -= 1
                        raise
                except BreakException as e:
                    if e.levels <= 1:
                        # Break out of this loop
                        break
                    else:
                        # Propagate to outer loop
                        e.levels -= 1
                        raise
        finally:
            self.loop_depth -= 1

        return last_exit_code

    def execute_while(self, stmt: WhileStatement) -> int:
        """
        Execute a while loop.

        Example:
            while test $i -lt 10; do echo $i; i=$((i+1)); done
        """
        last_exit_code = 0
        self.loop_depth += 1

        try:
            while True:
                # Evaluate condition
                cond_code = self.shell.execute(stmt.condition)

                # Exit if condition is false (non-zero)
                if cond_code != 0:
                    break

                # Execute loop body
                try:
                    last_exit_code = self.execute_block(stmt.body)
                except ContinueException as e:
                    if e.levels <= 1:
                        # Continue to next iteration
                        continue
                    else:
                        # Propagate to outer loop
                        e.levels -= 1
                        raise
                except BreakException as e:
                    if e.levels <= 1:
                        # Break out of this loop
                        break
                    else:
                        # Propagate to outer loop
                        e.levels -= 1
                        raise
        finally:
            self.loop_depth -= 1

        return last_exit_code

    def execute_until(self, stmt: UntilStatement) -> int:
        """
        Execute an until loop (opposite of while).

        Example:
            until test $i -ge 10; do echo $i; i=$((i+1)); done
        """
        last_exit_code = 0
        self.loop_depth += 1

        try:
            while True:
                # Evaluate condition
                cond_code = self.shell.execute(stmt.condition)

                # Exit if condition is true (zero)
                if cond_code == 0:
                    break

                # Execute loop body
                try:
                    last_exit_code = self.execute_block(stmt.body)
                except ContinueException as e:
                    if e.levels <= 1:
                        continue
                    else:
                        e.levels -= 1
                        raise
                except BreakException as e:
                    if e.levels <= 1:
                        break
                    else:
                        e.levels -= 1
                        raise
        finally:
            self.loop_depth -= 1

        return last_exit_code

    def execute_if(self, stmt: IfStatement) -> int:
        """
        Execute an if statement.

        Example:
            if test $x -eq 1; then echo one; elif test $x -eq 2; then echo two; else echo other; fi
        """
        # Try each branch
        for branch in stmt.branches:
            cond_code = self.shell.execute(branch.condition)

            if cond_code == 0:
                # Condition is true, execute this branch
                return self.execute_block(branch.body)

        # No branch matched, try else
        if stmt.else_body:
            return self.execute_block(stmt.else_body)

        return 0

    def execute_function_def(self, stmt: FunctionDefinition) -> int:
        """
        Register a function definition.

        Note: This doesn't execute the function, just stores it.
        """
        self.shell.functions[stmt.name] = {
            'name': stmt.name,
            'body': stmt.body,  # Store AST body
            'is_ast': True  # Flag to indicate AST-based function
        }
        return 0

    # ========================================================================
    # Function Execution
    # ========================================================================

    def execute_function_call(self, func_name: str, args: List[str]) -> int:
        """
        Execute a user-defined function.

        This handles:
        - Parameter passing ($1, $2, etc.)
        - Local variable scope management
        - _function_depth tracking for nested functions
        - Return value handling via ReturnException
        - Proper cleanup on exit

        Args:
            func_name: Name of the function to call
            args: Arguments to pass to the function

        Returns:
            Exit code from the function
        """
        if func_name not in self.shell.functions:
            return 127

        func_def = self.shell.functions[func_name]

        # Save current positional parameters
        saved_params = {}
        for key in list(self.shell.env.keys()):
            if key.isdigit() or key in ('#', '@', '*', '0'):
                saved_params[key] = self.shell.env[key]

        # Track function depth for local command
        current_depth = int(self.shell.env.get('_function_depth', '0'))
        self.shell.env['_function_depth'] = str(current_depth + 1)

        # Save local variables that will be shadowed
        saved_locals = {}
        for key in list(self.shell.env.keys()):
            if key.startswith('_local_'):
                saved_locals[key] = self.shell.env[key]

        # Set up function environment (positional parameters)
        self.shell.env['0'] = func_name
        self.shell.env['#'] = str(len(args))
        self.shell.env['@'] = ' '.join(args)
        self.shell.env['*'] = ' '.join(args)
        for i, arg in enumerate(args, 1):
            self.shell.env[str(i)] = arg

        # Push a new local scope
        if hasattr(self.shell, 'local_scopes'):
            self.shell.local_scopes.append({})

        self.function_depth += 1
        last_code = 0

        try:
            # Execute function body
            if func_def.get('is_ast', False):
                # AST-based function
                last_code = self.execute_block(func_def['body'])
            else:
                # Legacy list-based function (for backward compatibility)
                for cmd in func_def['body']:
                    last_code = self.shell.execute(cmd)

        except ReturnException as e:
            last_code = e.exit_code

        except (BreakException, ContinueException):
            self.shell.console.print(
                f"[red]{func_name}: break/continue only meaningful in a loop[/red]",
                highlight=False
            )
            last_code = 1

        finally:
            self.function_depth -= 1

            # Pop local scope
            if hasattr(self.shell, 'local_scopes') and self.shell.local_scopes:
                self.shell.local_scopes.pop()

            # Clear local variables from this function
            for key in list(self.shell.env.keys()):
                if key.startswith('_local_'):
                    del self.shell.env[key]

            # Restore saved local variables
            for key, value in saved_locals.items():
                self.shell.env[key] = value

            # Restore function depth
            self.shell.env['_function_depth'] = str(current_depth)
            if current_depth == 0:
                # Clean up if we're exiting the outermost function
                if '_function_depth' in self.shell.env:
                    del self.shell.env['_function_depth']

            # Restore positional parameters
            # First, remove all current positional params
            for key in list(self.shell.env.keys()):
                if key.isdigit() or key in ('#', '@', '*', '0'):
                    del self.shell.env[key]

            # Then restore saved ones
            self.shell.env.update(saved_params)

        return last_code

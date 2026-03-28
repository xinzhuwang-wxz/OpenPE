"""
Control flow exceptions for shell execution.

Using exceptions instead of exit codes for control flow provides:
1. Clean propagation through nested structures
2. Support for break N / continue N
3. Type safety and clear semantics
4. No confusion with actual command exit codes
"""


class ControlFlowException(Exception):
    """Base class for control flow exceptions"""
    pass


class BreakException(ControlFlowException):
    """
    Raised by 'break' command to exit loops.

    Attributes:
        levels: Number of loop levels to break out of (default 1)
                Decremented as it propagates through each loop level.

    Examples:
        break     -> BreakException(levels=1)  # exit innermost loop
        break 2   -> BreakException(levels=2)  # exit two levels of loops
    """

    def __init__(self, levels: int = 1):
        super().__init__(f"break {levels}")
        self.levels = max(1, levels)  # At least 1 level

    def __repr__(self):
        return f"BreakException(levels={self.levels})"


class ContinueException(ControlFlowException):
    """
    Raised by 'continue' command to skip to next iteration.

    Attributes:
        levels: Number of loop levels to skip (default 1)
                If levels > 1, continue affects an outer loop.

    Examples:
        continue     -> ContinueException(levels=1)  # continue innermost loop
        continue 2   -> ContinueException(levels=2)  # continue outer loop
    """

    def __init__(self, levels: int = 1):
        super().__init__(f"continue {levels}")
        self.levels = max(1, levels)

    def __repr__(self):
        return f"ContinueException(levels={self.levels})"


class ReturnException(ControlFlowException):
    """
    Raised by 'return' command to exit functions.

    Attributes:
        exit_code: Return value (exit code) for the function

    Examples:
        return      -> ReturnException(exit_code=0)
        return 1    -> ReturnException(exit_code=1)
    """

    def __init__(self, exit_code: int = 0):
        super().__init__(f"return {exit_code}")
        self.exit_code = exit_code

    def __repr__(self):
        return f"ReturnException(exit_code={self.exit_code})"

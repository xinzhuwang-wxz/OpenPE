"""Shell command parser for pipeline syntax"""

import shlex
import re
from typing import List, Tuple, Dict, Optional


class Redirection:
    """Represents a redirection operation"""
    def __init__(self, operator: str, target: str, fd: int = None):
        self.operator = operator  # '<', '>', '>>', '2>', '2>>', '&>', etc.
        self.target = target      # filename
        self.fd = fd             # file descriptor (0=stdin, 1=stdout, 2=stderr)


class CommandParser:
    """Parse shell command strings into pipeline components"""

    @staticmethod
    def _split_respecting_quotes(text: str, delimiter: str) -> List[str]:
        """
        Split a string by delimiter, but only when not inside quotes

        Args:
            text: String to split
            delimiter: Delimiter to split on (e.g., '|', '>')

        Returns:
            List of parts split by unquoted delimiters

        Example:
            >>> _split_respecting_quotes('echo "a | b" | wc', '|')
            ['echo "a | b" ', ' wc']
        """
        parts = []
        current_part = []
        in_single_quote = False
        in_double_quote = False
        escape_next = False
        i = 0

        while i < len(text):
            char = text[i]

            # Handle escape sequences
            if escape_next:
                current_part.append(char)
                escape_next = False
                i += 1
                continue

            if char == '\\':
                current_part.append(char)
                escape_next = True
                i += 1
                continue

            # Track quote state
            if char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
                current_part.append(char)
            elif char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
                current_part.append(char)
            # Check for delimiter when not in quotes
            elif not in_single_quote and not in_double_quote:
                # Check if we match the delimiter
                if text[i:i+len(delimiter)] == delimiter:
                    # Found delimiter outside quotes
                    parts.append(''.join(current_part))
                    current_part = []
                    i += len(delimiter)
                    continue
                else:
                    current_part.append(char)
            else:
                current_part.append(char)

            i += 1

        # Add the last part
        if current_part:
            parts.append(''.join(current_part))

        return parts

    @staticmethod
    def _find_redirections_respecting_quotes(command_line: str) -> Tuple[str, Dict[str, str]]:
        """
        Find redirection operators in command line, respecting quotes

        Args:
            command_line: Command line with possible redirections

        Returns:
            Tuple of (cleaned command, redirection dict)
        """
        redirections = {}

        # Parse character by character, tracking quote state
        result = []
        i = 0
        in_single_quote = False
        in_double_quote = False
        escape_next = False

        while i < len(command_line):
            char = command_line[i]

            # Handle escape sequences
            if escape_next:
                result.append(char)
                escape_next = False
                i += 1
                continue

            if char == '\\':
                result.append(char)
                escape_next = True
                i += 1
                continue

            # Track quote state
            if char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
                result.append(char)
                i += 1
            elif char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
                result.append(char)
                i += 1
            # Look for redirections when not in quotes
            elif not in_single_quote and not in_double_quote:
                # Try to match redirection operators (longest first)
                matched = False

                # Check for heredoc << (must be before <)
                if i < len(command_line) - 1 and command_line[i:i+2] == '<<':
                    # Find the delimiter
                    i += 2
                    # Skip whitespace
                    while i < len(command_line) and command_line[i] in ' \t':
                        i += 1
                    # Extract delimiter
                    delimiter = []
                    while i < len(command_line) and command_line[i] not in ' \t\n':
                        delimiter.append(command_line[i])
                        i += 1
                    if delimiter:
                        redirections['heredoc_delimiter'] = ''.join(delimiter)
                    matched = True

                # Check for 2>> (append stderr)
                elif i < len(command_line) - 2 and command_line[i:i+3] == '2>>':
                    i += 3
                    filename = CommandParser._extract_filename(command_line, i)
                    if filename:
                        redirections['stderr'] = filename[0]
                        redirections['stderr_mode'] = 'append'
                        i = filename[1]
                    matched = True

                # Check for 2> (stderr)
                elif i < len(command_line) - 1 and command_line[i:i+2] == '2>':
                    i += 2
                    filename = CommandParser._extract_filename(command_line, i)
                    if filename:
                        redirections['stderr'] = filename[0]
                        redirections['stderr_mode'] = 'write'
                        i = filename[1]
                    matched = True

                # Check for >> (append stdout)
                elif i < len(command_line) - 1 and command_line[i:i+2] == '>>':
                    i += 2
                    filename = CommandParser._extract_filename(command_line, i)
                    if filename:
                        redirections['stdout'] = filename[0]
                        redirections['stdout_mode'] = 'append'
                        i = filename[1]
                    matched = True

                # Check for > (stdout)
                elif command_line[i] == '>':
                    i += 1
                    filename = CommandParser._extract_filename(command_line, i)
                    if filename:
                        redirections['stdout'] = filename[0]
                        redirections['stdout_mode'] = 'write'
                        i = filename[1]
                    matched = True

                # Check for < (stdin)
                elif command_line[i] == '<':
                    i += 1
                    filename = CommandParser._extract_filename(command_line, i)
                    if filename:
                        redirections['stdin'] = filename[0]
                        i = filename[1]
                    matched = True

                if not matched:
                    result.append(char)
                    i += 1
            else:
                result.append(char)
                i += 1

        return ''.join(result).strip(), redirections

    @staticmethod
    def _extract_filename(command_line: str, start_pos: int) -> Optional[Tuple[str, int]]:
        """
        Extract filename after a redirection operator

        Args:
            command_line: Full command line
            start_pos: Position to start looking for filename

        Returns:
            Tuple of (filename, new_position) or None
        """
        i = start_pos

        # Skip whitespace
        while i < len(command_line) and command_line[i] in ' \t':
            i += 1

        if i >= len(command_line):
            return None

        filename = []
        in_quotes = None

        # Check if filename is quoted
        if command_line[i] in ('"', "'"):
            in_quotes = command_line[i]
            i += 1
            # Read until closing quote
            while i < len(command_line):
                if command_line[i] == in_quotes:
                    i += 1
                    break
                filename.append(command_line[i])
                i += 1
        else:
            # Read until whitespace or special character
            while i < len(command_line) and command_line[i] not in ' \t\n|<>;&':
                filename.append(command_line[i])
                i += 1

        if filename:
            return (''.join(filename), i)
        return None

    @staticmethod
    def parse_command_line(command_line: str) -> Tuple[List[Tuple[str, List[str]]], Dict]:
        """
        Parse a complete command line with pipelines and redirections
        Now with quote-aware parsing!

        Args:
            command_line: Full command line string

        Returns:
            Tuple of (pipeline_commands, global_redirections)

        Example:
            >>> parse_command_line('echo "a | b" | wc > out.txt')
            ([('echo', ['a | b']), ('wc', [])], {'stdout': 'out.txt', 'stdout_mode': 'write'})
        """
        # First, extract global redirections (those at the end of the pipeline)
        # Use the new quote-aware redirection parser
        command_line, redirections = CommandParser.parse_redirection(command_line)

        # Then parse the pipeline
        commands = CommandParser.parse_pipeline(command_line)

        return commands, redirections

    @staticmethod
    def parse_pipeline(command_line: str) -> List[Tuple[str, List[str]]]:
        """
        Parse a command line into pipeline components
        Now respects quotes! Pipes inside quotes are preserved.

        Args:
            command_line: Command line string (e.g., "cat file.txt | grep pattern | wc -l")

        Returns:
            List of (command, args) tuples

        Example:
            >>> parser.parse_pipeline('echo "This | that" | wc')
            [('echo', ['This | that']), ('wc', [])]
        """
        if not command_line.strip():
            return []

        # Use quote-aware splitting instead of simple split('|')
        pipeline_parts = CommandParser._split_respecting_quotes(command_line, '|')

        commands = []
        for part in pipeline_parts:
            part = part.strip()
            if not part:
                continue

            # Use shlex to properly handle quoted strings
            try:
                tokens = shlex.split(part)
            except ValueError as e:
                # If shlex fails (unmatched quotes), fall back to simple split
                tokens = part.split()

            if tokens:
                command = tokens[0]
                args = tokens[1:] if len(tokens) > 1 else []
                commands.append((command, args))

        return commands

    @staticmethod
    def parse_redirection(command_line: str) -> Tuple[str, Dict[str, str]]:
        """
        Parse redirection operators
        Now respects quotes! Redirections inside quotes are preserved.

        Args:
            command_line: Command line with possible redirections

        Returns:
            Tuple of (cleaned command, redirection dict)
            Redirection dict keys: 'stdin', 'stdout', 'stderr', 'stdout_mode', 'heredoc_delimiter'

        Example:
            >>> parse_redirection('echo "Look at this arrow ->" > file.txt')
            ('echo "Look at this arrow ->"', {'stdout': 'file.txt', 'stdout_mode': 'write'})
        """
        # Use the new quote-aware redirection finder
        return CommandParser._find_redirections_respecting_quotes(command_line)

    @staticmethod
    def quote_arg(arg: str) -> str:
        """Quote an argument if it contains spaces or special characters"""
        if ' ' in arg or any(c in arg for c in '|&;<>()$`\\"\''):
            return shlex.quote(arg)
        return arg

    @staticmethod
    def unquote_arg(arg: str) -> str:
        """Remove quotes from an argument"""
        if (arg.startswith('"') and arg.endswith('"')) or \
           (arg.startswith("'") and arg.endswith("'")):
            return arg[1:-1]
        return arg

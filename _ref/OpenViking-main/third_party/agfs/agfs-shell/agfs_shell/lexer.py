"""
Robust lexer for shell command parsing

This module provides a unified lexer that handles:
- Quote tracking (single and double quotes)
- Escape sequences
- Comment detection
- Token splitting

Replaces fragile manual character-by-character parsing throughout the codebase.
"""

from typing import List, Tuple, Optional
from enum import Enum


class TokenType(Enum):
    """Types of tokens the lexer can produce"""
    WORD = "word"
    PIPE = "pipe"
    REDIRECT = "redirect"
    COMMENT = "comment"
    EOF = "eof"


class Token:
    """A single lexical token"""

    def __init__(self, type: TokenType, value: str, position: int = 0):
        self.type = type
        self.value = value
        self.position = position

    def __repr__(self):
        return f"Token({self.type.value}, {repr(self.value)}, pos={self.position})"

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.value == other.value


class ShellLexer:
    """
    Robust lexer for shell commands

    Handles quotes, escapes, and special characters correctly.
    """

    def __init__(self, text: str):
        """
        Initialize lexer with text to parse

        Args:
            text: Shell command line to tokenize
        """
        self.text = text
        self.pos = 0
        self.length = len(text)

    def peek(self, offset: int = 0) -> Optional[str]:
        """Look ahead at character without consuming it"""
        pos = self.pos + offset
        if pos < self.length:
            return self.text[pos]
        return None

    def advance(self) -> Optional[str]:
        """Consume and return current character"""
        if self.pos < self.length:
            char = self.text[self.pos]
            self.pos += 1
            return char
        return None

    def skip_whitespace(self):
        """Skip over whitespace characters"""
        while self.peek() and self.peek() in ' \t':
            self.advance()

    def read_quoted_string(self, quote_char: str) -> str:
        """
        Read a quoted string, handling escapes

        Args:
            quote_char: Quote character (' or ")

        Returns:
            Content of quoted string (without quotes)
        """
        result = []
        # Skip opening quote
        self.advance()

        while True:
            char = self.peek()

            if char is None:
                # Unclosed quote - return what we have
                break

            if char == '\\' and quote_char == '"':
                # Escape sequence in double quotes
                self.advance()
                next_char = self.advance()
                if next_char:
                    result.append(next_char)
            elif char == quote_char:
                # Closing quote
                self.advance()
                break
            else:
                result.append(char)
                self.advance()

        return ''.join(result)

    def read_word(self) -> str:
        """
        Read a word token, respecting quotes and escapes

        Returns:
            Word content
        """
        result = []

        while True:
            char = self.peek()

            if char is None:
                break

            # Check for special characters that end a word
            if char in ' \t\n|<>;&':
                break

            # Handle quotes
            if char == '"':
                quoted = self.read_quoted_string('"')
                result.append(quoted)
            elif char == "'":
                quoted = self.read_quoted_string("'")
                result.append(quoted)
            # Handle escapes
            elif char == '\\':
                self.advance()
                next_char = self.advance()
                if next_char:
                    result.append(next_char)
            else:
                result.append(char)
                self.advance()

        return ''.join(result)

    def tokenize(self) -> List[Token]:
        """
        Tokenize the entire input

        Returns:
            List of tokens
        """
        tokens = []

        while self.pos < self.length:
            self.skip_whitespace()

            if self.pos >= self.length:
                break

            char = self.peek()
            start_pos = self.pos

            # Check for comments
            if char == '#':
                # Read to end of line
                comment = []
                while self.peek() and self.peek() != '\n':
                    comment.append(self.advance())
                tokens.append(Token(TokenType.COMMENT, ''.join(comment), start_pos))
                continue

            # Check for pipe
            if char == '|':
                self.advance()
                tokens.append(Token(TokenType.PIPE, '|', start_pos))
                continue

            # Check for redirections
            if char == '>':
                redir = self.advance()
                if self.peek() == '>':
                    redir += self.advance()
                tokens.append(Token(TokenType.REDIRECT, redir, start_pos))
                continue

            if char == '<':
                redir = self.advance()
                if self.peek() == '<':
                    redir += self.advance()
                tokens.append(Token(TokenType.REDIRECT, redir, start_pos))
                continue

            if char == '2':
                if self.peek(1) == '>':
                    redir = self.advance() + self.advance()
                    if self.peek() == '>':
                        redir += self.advance()
                    tokens.append(Token(TokenType.REDIRECT, redir, start_pos))
                    continue

            # Otherwise, read a word
            word = self.read_word()
            if word:
                tokens.append(Token(TokenType.WORD, word, start_pos))

        tokens.append(Token(TokenType.EOF, '', self.pos))
        return tokens


class QuoteTracker:
    """
    Utility class to track quote state while parsing

    Use this when you need to manually parse but need to know if you're inside quotes.
    """

    def __init__(self):
        self.in_single_quote = False
        self.in_double_quote = False
        self.escape_next = False

    def process_char(self, char: str):
        """
        Update quote state based on character

        Args:
            char: Current character being processed
        """
        if self.escape_next:
            self.escape_next = False
            return

        if char == '\\':
            self.escape_next = True
            return

        if char == '"' and not self.in_single_quote:
            self.in_double_quote = not self.in_double_quote
        elif char == "'" and not self.in_double_quote:
            self.in_single_quote = not self.in_single_quote

    def is_quoted(self) -> bool:
        """Check if currently inside any type of quotes"""
        return self.in_single_quote or self.in_double_quote

    def reset(self):
        """Reset quote tracking state"""
        self.in_single_quote = False
        self.in_double_quote = False
        self.escape_next = False


def strip_comments(line: str, comment_chars: str = '#') -> str:
    """
    Strip comments from a line, respecting quotes

    Args:
        line: Line to process
        comment_chars: Characters that start comments (default: '#')

    Returns:
        Line with comments removed

    Example:
        >>> strip_comments('echo "test # not a comment" # real comment')
        'echo "test # not a comment" '
    """
    tracker = QuoteTracker()
    result = []

    for i, char in enumerate(line):
        tracker.process_char(char)

        # Check if this starts a comment (when not quoted)
        if char in comment_chars and not tracker.is_quoted():
            break

        result.append(char)

    return ''.join(result).rstrip()


def split_respecting_quotes(text: str, delimiter: str) -> List[str]:
    """
    Split text by delimiter, but only when not inside quotes

    This is a utility function that uses QuoteTracker.
    For more complex parsing, use ShellLexer instead.

    Args:
        text: Text to split
        delimiter: Delimiter to split on

    Returns:
        List of parts

    Example:
        >>> split_respecting_quotes('echo "a | b" | wc', '|')
        ['echo "a | b" ', ' wc']
    """
    tracker = QuoteTracker()
    parts = []
    current = []
    i = 0

    while i < len(text):
        char = text[i]
        tracker.process_char(char)

        # Check for delimiter when not quoted
        if not tracker.is_quoted() and text[i:i+len(delimiter)] == delimiter:
            parts.append(''.join(current))
            current = []
            i += len(delimiter)
        else:
            current.append(char)
            i += 1

    if current:
        parts.append(''.join(current))

    return parts

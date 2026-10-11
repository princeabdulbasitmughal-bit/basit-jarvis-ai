"""
Custom exceptions for the Factorial Service package.
"""

class FactorialError(Exception):
    """Base exception for all factorial computation errors."""
    pass


class InvalidInputError(FactorialError, ValueError):
    """Raised when the input provided to factorial computation is invalid."""
    pass


class ExceedsMaximumInputError(FactorialError, ValueError):
    """Raised when the input integer exceeds the maximum allowed threshold."""
    pass

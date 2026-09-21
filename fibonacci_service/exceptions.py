"""
Domain-specific exceptions for Fibonacci computations.
"""


class FibonacciError(Exception):
    """Base exception for all Fibonacci calculation errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NegativeIntegerError(FibonacciError):
    """Raised when an index n < 0 is provided."""

    def __init__(self, n: int) -> None:
        self.n = n
        super().__init__(
            f"Fibonacci sequence index must be non-negative (n >= 0). Received: {n}"
        )


class ValueTooLargeError(FibonacciError):
    """Raised when the requested index exceeds safety/memory thresholds."""

    def __init__(self, n: int, max_limit: int) -> None:
        self.n = n
        self.max_limit = max_limit
        super().__init__(
            f"Requested index n={n} exceeds maximum configured limit of {max_limit}."
        )

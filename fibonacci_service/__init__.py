"""
Fibonacci Service Package.

High-performance, production-ready suite for computing Fibonacci numbers,
sequences, and mathematical properties with O(log n) fast doubling algorithms,
REST APIs, CLI tools, and comprehensive error handling.
"""

__version__ = "2.1.0"
__author__ = "Basit1 v2.1"

from fibonacci_service.core import (
    Algorithm,
    FibonacciCalculator,
    fast_doubling,
    iterative_fibonacci,
    matrix_fibonacci,
    memoized_fibonacci,
)
from fibonacci_service.exceptions import (
    FibonacciError,
    NegativeIntegerError,
    ValueTooLargeError,
)

__all__ = [
    "Algorithm",
    "FibonacciCalculator",
    "fast_doubling",
    "iterative_fibonacci",
    "matrix_fibonacci",
    "memoized_fibonacci",
    "FibonacciError",
    "NegativeIntegerError",
    "ValueTooLargeError",
]

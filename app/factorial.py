def compute_factorial(n: int) -> int:
    """
    Compute the factorial of a non-negative integer n.

    Args:
        n (int): A non-negative integer.

    Returns:
        int: The factorial of n.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    if n == 0:
        return 1
    factorial = 1
    for i in range(1, n + 1):
        factorial *= i
    return factorial

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python factorial.py <number>")
        sys.exit(1)
    try:
        num = int(sys.argv[1])
        result = compute_factorial(num)
        print(f"The factorial of {num} is {result}.")
    except ValueError as e:
        print(f"Error: {e}")

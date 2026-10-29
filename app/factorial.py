def factorial(n):
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
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python factorial.py <number>")
        sys.exit(1)
    try:
        num = int(sys.argv[1])
        print(f"The factorial of {num} is {factorial(num)}")
    except ValueError as e:
        print(f"Error: {e}")

import unittest
from app.factorial import compute_factorial

class TestFactorial(unittest.TestCase):
    def test_factorial_of_zero(self):
        self.assertEqual(compute_factorial(0), 1)

    def test_factorial_of_positive_integer(self):
        self.assertEqual(compute_factorial(5), 120)

    def test_factorial_of_negative_integer(self):
        with self.assertRaises(ValueError):
            compute_factorial(-1)

if __name__ == "__main__":
    unittest.main()

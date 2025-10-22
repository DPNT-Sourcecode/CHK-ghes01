import pytest
from solutions.CHK.checkout_solution import CheckoutSolution


class TestSum:
    @pytest.mark.parametrize(
        "items,expected",
        [
            ("A", 50),
            ("B", 30),
            ("C", 20),
            ("D", 15),
            ("AA", 100),
            ("AAA", 130),
            ("AAAA", 180),
            ("AAAAA", 130 + 50 * 2),
            ("AAAAAA", 130 * 2),
            ("BB", 45),
            ("BBB", 75),
            ("BBBB", 90),
            ("ABCD", 115),
            ("", 0),
            ("INVALID", -1),
        ],
    )
    def test_checkout(self, items, expected):
        assert CheckoutSolution().checkout(items) == expected




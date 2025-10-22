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
            ("AAAAA", 200),
            ("AAAAAA", 250),
            ("BB", 45),
            ("BBB", 75),
            ("BBBB", 90),
            ("ABCD", 115),
            ("", 0),
        ],
    )
    def test_checkout(self, items, expected):
        assert CheckoutSolution().checkout(items) == expected



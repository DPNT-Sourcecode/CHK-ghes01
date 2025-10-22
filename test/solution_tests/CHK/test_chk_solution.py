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
            ("E", 40),
            ("AA", 100),
            ("AAA", 130),
            ("AAAA", 180),
            ("AAAAA", 200),
            ("AAAAAA", 250),
            ("AAAAAAA", 300),
            ("AAAAAAAA", 330),
            ("BB", 45),
            ("BBB", 75),
            ("BBBB", 90),
            ("EE", 80),
            ("EEB", 80),
            ("EEEB", 120),
            ("EEBB", 110),
            ("EEEEBB", 160),
            ("ABCD", 115),
            ("ABCDE", 155),
            ("", 0),
            ("INVALID", -1),
        ],
    )
    def test_checkout(self, items: str, expected: int) -> None:
        assert CheckoutSolution().checkout(items) == expected


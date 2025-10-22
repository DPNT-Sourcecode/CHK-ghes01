import pytest
from solutions.CHK.checkout_solution import CheckoutSolution


class TestSum:
    @pytest.mark.parametrize(
        "items,expected",
        [
            # Single items
            ("A", 50),
            ("B", 30),
            ("C", 20),
            ("D", 15),
            ("E", 40),
            # Item A multi-price offers: 5A for 200, 3A for 130, 1A for 50
            ("AA", 2 * 50),
            ("AAA", 130),
            ("AAAA", 130 + 50),
            ("AAAAA", 200),
            ("AAAAAA", 200 + 50),
            ("AAAAAAA", 200 + 2 * 50),
            ("AAAAAAAA", 200 + 130),
            ("AAAAAAAAA", 200 + 130 + 50),
            ("AAAAAAAAAA", 2 * 200),
            # Item B multi-price offers: 2B for 45, 1B for 30
            ("BB", 45),
            ("BBB", 45 + 30),
            ("BBBB", 2 * 45),
            ("BBBBB", 2 * 45 + 30),
            # Item E - buy 2E get 1B free: 1E for 40
            ("EE", 2 * 40),
            ("EEB", 2 * 40 + 0),  # 2E + 1B (free)
            ("EEBB", 2 * 40 + 30),  # 2E + 2B (1 free, 1 paid)
            ("EEEB", 3 * 40 + 0),  # 3E + 1B (free)
            ("EEEEBB", 4 * 40 + 0),  # 4E + 2B (both free)
            ("EEEEBBB", 4 * 40 + 30),  # 4E + 3B (2 free, 1 paid)
            ("EEEEBBBB", 4 * 40 + 45),  # 4E + 4B (2 free, 2 paid with offer)
            ("BEBEEE", 4 * 40 + 0),  # Order shouldn't matter: 4E + 2B (both free)
            # Mixed items
            ("ABCD", 50 + 30 + 20 + 15),
            ("ABCDE", 50 + 30 + 20 + 15 + 40),
            (
                "ABCDEABCDE",
                2 * 50 + 30 + 2 * 20 + 2 * 15 + 2 * 40,
            ),  # 2A, 2B (1 free), 2C, 2D, 2E
            # Edge cases
            ("", 0),
            ("INVALID", -1),
            ("A1", -1),
            ("a", -1),
            ("ABCa", -1),
            # Edge case: More E's than B's
            ("EEEEEEEB", 7 * 40 + 0),  # 7E + 1B (free since 7E gives 3 free B's)
            # Edge case: B offer + E offer combination
            ("EEEEBB", 4 * 40 + 0),  # 4E gives 2 free B's, so both B's are free
            (
                "EEEEBBBB",
                4 * 40 + 45,
            ),  # 4E gives 2 free B's, remaining 2B's get the offer
            (
                "EEBBBB",
                2 * 40 + 45 + 30,
            ),  # 2E gives 1 free B, remaining 3B's = 1 offer + 1 single
        ],
    )
    def test_checkout(self, items, expected):
        assert CheckoutSolution().checkout(items) == expected



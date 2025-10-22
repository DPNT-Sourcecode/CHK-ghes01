from collections import Counter

import pytest
from solutions.CHK.checkout_solution import (
    CheckoutSolution,
    FreeItemOffer,
    MultiBuyOffer,
)

from lib.solutions.CHK.checkout_solution import GroupDiscountOffer, GroupOfferResult


class TestCheckout:
    @pytest.mark.parametrize(
        "items,expected",
        [
            # Single items
            ("A", 50),
            ("B", 30),
            ("C", 20),
            ("D", 15),
            ("E", 40),
            ("F", 10),
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
            # Item F - buy 2F get 1F free (requires 3 total): 1F for 10
            ("FF", 2 * 10),
            ("FFF", 2 * 10),  # 3F: pay for 2, get 1 free
            ("FFFF", 3 * 10),  # 4F: pay for 3
            ("FFFFF", 4 * 10),  # 5F: pay for 4
            ("FFFFFF", 4 * 10),  # 6F: pay for 4 (2 groups of 3)
            ("FFFFFFF", 5 * 10),  # 7F: pay for 5
            ("FFFFFFFF", 6 * 10),  # 8F: pay for 6
            ("FFFFFFFFF", 6 * 10),  # 9F: pay for 6 (3 groups of 3)
            # Mixed items
            ("ABCD", 50 + 30 + 20 + 15),
            ("ABCDE", 50 + 30 + 20 + 15 + 40),
            (
                "ABCDEABCDE",
                2 * 50 + 30 + 2 * 20 + 2 * 15 + 2 * 40,
            ),  # 2A, 2B (1 free), 2C, 2D, 2E
            # Edge cases
            ("", 0),
            ("INVALID!", -1),
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


class TestParseSKUs:
    @pytest.mark.parametrize(
        "skus,expected",
        [
            ("", Counter()),
            ("A", Counter({"A": 1})),
            ("AAA", Counter({"A": 3})),
            ("ABC", Counter({"A": 1, "B": 1, "C": 1})),
        ],
    )
    def test_parse_valid_skus(self, skus, expected):
        solution = CheckoutSolution()
        assert solution.parse_skus(skus) == expected

    @pytest.mark.parametrize("skus", ["a", "1", "!", "ABCx"])
    def test_parse_invalid_skus(self, skus):
        solution = CheckoutSolution()
        with pytest.raises(ValueError):
            solution.parse_skus(skus)


class TestApplyFreeItemOffers:
    @pytest.mark.parametrize(
        "items,offers,expected",
        [
            (
                Counter({"E": 2, "B": 1}),
                [FreeItemOffer(sku="E", quantity=2, gift_sku="B", gift_quantity=1)],
                Counter({"E": 2, "B": 0}),
            ),
            (
                Counter({"E": 4, "B": 3}),
                [FreeItemOffer(sku="E", quantity=2, gift_sku="B", gift_quantity=1)],
                Counter({"E": 4, "B": 1}),
            ),
            (
                Counter({"F": 3}),
                [FreeItemOffer(sku="F", quantity=3, gift_sku="F", gift_quantity=1)],
                Counter({"F": 2}),
            ),
        ],
    )
    def test_apply_free_offers(self, items, offers, expected):
        solution = CheckoutSolution()
        result = solution.apply_free_item_offers(items, offers)
        assert result == expected


class TestCalculateSKUCost:
    @pytest.mark.parametrize(
        "sku,num_items,base_prices,multibuy_offers,expected",
        [
            pytest.param("C", 3, {"C": 20}, {}, 60, id="no_offer"),
            pytest.param(
                "B",
                3,
                {"B": 30},
                {"B": [MultiBuyOffer(quantity=2, price=45)]},
                75,
                id="single_multibuy_offer",
            ),
            pytest.param(
                "A",
                8,
                {"A": 50},
                {
                    "A": [
                        MultiBuyOffer(quantity=5, price=200),
                        MultiBuyOffer(quantity=3, price=130),
                    ]
                },
                330,
                id="multiple_multibuy_offers",
            ),
        ],
    )
    def test_calculate_sku_cost(
        self, sku, num_items, base_prices, multibuy_offers, expected
    ):
        solution = CheckoutSolution()
        cost = solution.calculate_sku_cost(sku, num_items, base_prices, multibuy_offers)
        assert cost == expected


class TestCalculateMultibuyCost:
    @pytest.mark.parametrize(
        "items,expected",
        [
            (Counter({"A": 3, "B": 2, "C": 1}), 130 + 45 + 20),
            (Counter(), 0),
        ],
    )
    def test_calculate_multibuy_cost(self, items, expected):
        solution = CheckoutSolution()
        result = solution.calculate_multibuy_cost(items, solution.multibuy_offers)
        assert result == expected


class TestApplyGroupBuyOffers:
    @pytest.mark.parametrize(
        "items,offers,expected",
        [
            (
                Counter({"A": 3, "B": 2, "C": 1}),
                [],
                GroupOfferResult(
                    remaining_items=Counter({"A": 3, "B": 2, "C": 1}), offer_cost=0
                ),
            ),
        ],
    )
    def test_apply_group_buy_offers(self, items, offers, expected):
        solution = CheckoutSolution()
        result = solution.apply_group_buy_offers(items, offers)
        assert result == expected



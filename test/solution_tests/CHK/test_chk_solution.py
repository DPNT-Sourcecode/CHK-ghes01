from collections import Counter

import pytest
from solutions.CHK.checkout_solution import (
    CheckoutSolution,
    FreeItemOffer,
    MultiBuyOffer,
)

from lib.solutions.CHK.checkout_solution import GroupDiscountOffer, GroupOfferResult


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
        base_prices = {"A": 50, "B": 30, "C": 20}
        assert solution.parse_skus(skus, base_prices) == expected

    @pytest.mark.parametrize("skus", ["a", "1", "!", "ABCx"])
    def test_parse_invalid_skus(self, skus):
        solution = CheckoutSolution()
        base_prices = {"A": 50, "B": 30, "C": 20}
        with pytest.raises(ValueError):
            solution.parse_skus(skus, base_prices)


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
        base_prices = {"A": 50, "B": 30, "C": 20}
        multibuy_offers = {
            "A": [MultiBuyOffer(quantity=3, price=130)],
            "B": [MultiBuyOffer(quantity=2, price=45)],
        }
        result = solution.calculate_multibuy_cost(items, base_prices, multibuy_offers)
        assert result == expected


class TestApplyGroupBuyOffers:
    @pytest.mark.parametrize(
        "items,offers,expected",
        [
            (
                Counter("ABC"),
                [],
                GroupOfferResult(remaining_items=Counter("ABC"), offer_cost=0),
            ),
            (
                Counter("AAB"),
                [GroupDiscountOffer(skus=["A", "B"], quantity=2, price=1)],
                GroupOfferResult(remaining_items=Counter("B"), offer_cost=1),
            ),
            (
                Counter("AAB"),
                [GroupDiscountOffer(skus=["B", "A"], quantity=2, price=1)],
                GroupOfferResult(remaining_items=Counter("A"), offer_cost=1),
            ),
        ],
    )
    def test_apply_group_buy_offers(self, items, offers, expected):
        solution = CheckoutSolution()
        result = solution.calculate_group_offer_discount(items, offers)
        assert result.remaining_items == expected.remaining_items
        assert result.offer_cost == expected.offer_cost







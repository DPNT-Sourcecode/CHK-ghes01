from collections import Counter

from pydantic import BaseModel, field_validator


class MultiBuyOffer(BaseModel, frozen=True):
    quantity: int
    price: int


class FreeItemOffer(BaseModel, frozen=True):
    sku: str
    quantity: int
    gift_sku: str
    gift_quantity: int


class GroupDiscountOffer(BaseModel, frozen=True):
    """Any quantity of skus for price.

    Note: skus should be ordered from most to least expensive.
    """

    skus: list[str]
    quantity: int
    price: int


class GroupOfferResult(BaseModel, frozen=True):
    remaining_items: Counter[str]
    offer_cost: int

    @field_validator("remaining_items", mode="before")
    @classmethod
    def normalize_counter(cls, v: Counter[str]) -> Counter[str]:
        # Remove zero and negative counts
        return +v


# Default constants
DEFAULT_FREE_ITEM_OFFERS = [
    FreeItemOffer(sku="E", quantity=2, gift_sku="B", gift_quantity=1),
    FreeItemOffer(
        sku="F", quantity=3, gift_sku="F", gift_quantity=1
    ),  # buy 2 F get 1 F free
    FreeItemOffer(sku="N", quantity=3, gift_sku="M", gift_quantity=1),
    FreeItemOffer(sku="R", quantity=3, gift_sku="Q", gift_quantity=1),
    FreeItemOffer(
        sku="U", quantity=4, gift_sku="U", gift_quantity=1
    ),  # buy 3 U get 1 U free
]

DEFAULT_MULTIBUY_OFFERS = {
    "A": [
        MultiBuyOffer(quantity=5, price=200),
        MultiBuyOffer(quantity=3, price=130),
    ],
    "B": [MultiBuyOffer(quantity=2, price=45)],
    "H": [
        MultiBuyOffer(quantity=10, price=80),
        MultiBuyOffer(quantity=5, price=45),
    ],
    "K": [MultiBuyOffer(quantity=2, price=120)],
    "P": [MultiBuyOffer(quantity=5, price=200)],
    "Q": [MultiBuyOffer(quantity=3, price=80)],
    "V": [
        MultiBuyOffer(quantity=3, price=130),
        MultiBuyOffer(quantity=2, price=90),
    ],
}

DEFAULT_GROUP_DISCOUNT_OFFERS = [
    # Buy any 3 of (S,T,X,Y,Z) for 45
    # Ordered by price descending: Z(21), S(20), T(20), Y(20), X(17)
    GroupDiscountOffer(skus=["Z", "S", "T", "Y", "X"], quantity=3, price=45),
]

DEFAULT_BASE_PRICES = {
    "A": 50,
    "B": 30,
    "C": 20,
    "D": 15,
    "E": 40,
    "F": 10,
    "G": 20,
    "H": 10,
    "I": 35,
    "J": 60,
    "K": 70,
    "L": 90,
    "M": 15,
    "N": 40,
    "O": 10,
    "P": 50,
    "Q": 30,
    "R": 50,
    "S": 20,
    "T": 20,
    "U": 40,
    "V": 50,
    "W": 20,
    "X": 17,
    "Y": 20,
    "Z": 21,
}


class CheckoutSolution:
    def __init__(
        self,
        free_item_offers: list[FreeItemOffer] | None = None,
        multibuy_offers: dict[str, list[MultiBuyOffer]] | None = None,
        group_discount_offers: list[GroupDiscountOffer] | None = None,
        base_prices: dict[str, int] | None = None,
    ):
        # Define free item offers
        self.free_item_offers = (
            free_item_offers
            if free_item_offers is not None
            else DEFAULT_FREE_ITEM_OFFERS
        )

        # Define multibuy offers per SKU (sorted by quantity descending)
        self.multibuy_offers = (
            multibuy_offers if multibuy_offers is not None else DEFAULT_MULTIBUY_OFFERS
        )

        # Define group discount offers
        self.group_discount_offers = (
            group_discount_offers
            if group_discount_offers is not None
            else DEFAULT_GROUP_DISCOUNT_OFFERS
        )

        # Define base prices
        self.base_prices = (
            base_prices if base_prices is not None else DEFAULT_BASE_PRICES
        )

    @staticmethod
    def parse_skus(skus: str, base_prices: dict[str, int]) -> Counter[str]:
        """Parse SKU string into a Counter of items."""
        counter = Counter(skus)
        # Check that all SKUs are valid
        for sku in counter:
            if sku not in base_prices:
                raise ValueError(f"Invalid SKU: {sku}")
        return counter

    @staticmethod
    def apply_free_item_offers(
        items: Counter[str], offers: list[FreeItemOffer]
    ) -> Counter[str]:
        """Apply free item offers to the item counts.

        Note: We assume there are no cycles in the Buy N get X offers.
        """
        items = items.copy()
        for offer in offers:
            if offer.sku in items:
                free_items = (items[offer.sku] // offer.quantity) * offer.gift_quantity
                items[offer.gift_sku] = max(0, items[offer.gift_sku] - free_items)
        return items

    @staticmethod
    def calculate_group_offer_discount(
        items: Counter[str],
        offers: list[GroupDiscountOffer],
    ) -> GroupOfferResult:
        """Apply group offers to the item counts.

        Note: We assume group buy offers are disjoint from other offer types (free item offers, multibuy offers).
        Items in group buy offers should not participate in other promotional schemes.

        Our policy is to favor the customer, hence we should remove the most expensive items
        in the group buy offers first to maximize their discount benefit.

        Group buy offers are ordered from most expensive skus to the least.
        """
        items = items.copy()
        total_offer_cost = 0

        for offer in offers:
            # Count how many items we have that are part of this offer
            available_items: Counter[str] = Counter()
            for sku in offer.skus:
                if sku in items:
                    available_items[sku] = items[sku]

            # Calculate how many times we can apply this offer
            total_available = sum(available_items.values())
            num_offers = total_available // offer.quantity

            if num_offers > 0:
                items_to_remove = num_offers * offer.quantity
                # remove most expensive skus first
                for sku in offer.skus:
                    if items_to_remove == 0:
                        break
                    if sku in items and items[sku] > 0:
                        removed = min(items[sku], items_to_remove)
                        items[sku] -= removed
                        items_to_remove -= removed

                total_offer_cost += num_offers * offer.price

        return GroupOfferResult(remaining_items=items, offer_cost=total_offer_cost)

    @staticmethod
    def calculate_multibuy_cost(
        items: Counter[str],
        base_prices: dict[str, int],
        multibuy_offers: dict[str, list[MultiBuyOffer]],
    ) -> int:
        """Calculate cost for items with multibuy offers applied."""
        total_cost = 0

        for sku, num_items in items.items():
            if sku in multibuy_offers:
                remaining = num_items
                for offer in multibuy_offers[sku]:
                    total_cost += (remaining // offer.quantity) * offer.price
                    remaining = remaining % offer.quantity
                # Add cost for remaining items at base price
                total_cost += remaining * base_prices[sku]
            else:
                # No multibuy offer, use base price
                total_cost += num_items * base_prices[sku]

        return total_cost

    @staticmethod
    def calculate_sku_cost(
        sku: str,
        num_items: int,
        base_prices: dict[str, int],
        multibuy_offers: dict[str, list[MultiBuyOffer]],
    ) -> int:
        """Calculate total cost for a single SKU including multibuy offers."""
        if sku not in base_prices:
            raise ValueError("Invalid SKU")

        cost = 0
        remaining = num_items

        # Apply multibuy offers if available
        if sku in multibuy_offers:
            for offer in multibuy_offers[sku]:
                cost += (remaining // offer.quantity) * offer.price
                remaining = remaining % offer.quantity

        # Add cost for remaining items at base price
        cost += remaining * base_prices[sku]
        return cost

    def calculate_total_cost(
        self,
        items: Counter[str],
        base_prices: dict[str, int],
        multibuy_offers: dict[str, list[MultiBuyOffer]],
    ) -> int:
        """Calculate total cost for all items."""
        total_cost = 0
        for sku, num_items in items.items():
            cost = self.calculate_sku_cost(sku, num_items, base_prices, multibuy_offers)
            total_cost += cost
        return total_cost

    def checkout(self, skus: str) -> int:
        # skus = unicode string
        try:
            # Parse SKUs into item counts
            ordered_items = self.parse_skus(skus, self.base_prices)
        except ValueError:
            return -1

        # Apply free item offers
        ordered_items = self.apply_free_item_offers(
            ordered_items, self.free_item_offers
        )

        # Apply group discount offers
        group_result = self.calculate_group_offer_discount(
            ordered_items, self.group_discount_offers
        )
        total_cost = group_result.offer_cost

        # Calculate cost for remaining items with multibuy offers
        total_cost += self.calculate_multibuy_cost(
            group_result.remaining_items, self.base_prices, self.multibuy_offers
        )

        return total_cost




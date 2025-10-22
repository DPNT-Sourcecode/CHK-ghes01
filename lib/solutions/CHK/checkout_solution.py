from collections import Counter

from pydantic import BaseModel


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


class CheckoutSolution:
    def __init__(self):
        # Define free item offers
        self.free_item_offers = [
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

        # Define multibuy offers per SKU (sorted by quantity descending)
        self.multibuy_offers = {
            "A": [
                MultiBuyOffer(quantity=5, price=200),
                MultiBuyOffer(quantity=3, price=130),
            ],
            "B": [MultiBuyOffer(quantity=2, price=45)],
            "H": [
                MultiBuyOffer(quantity=10, price=80),
                MultiBuyOffer(quantity=5, price=45),
            ],
            "K": [MultiBuyOffer(quantity=2, price=150)],
            "P": [MultiBuyOffer(quantity=5, price=200)],
            "Q": [MultiBuyOffer(quantity=3, price=80)],
            "V": [
                MultiBuyOffer(quantity=3, price=130),
                MultiBuyOffer(quantity=2, price=90),
            ],
        }

        # Define base prices
        self.base_prices = {
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
            "K": 80,
            "L": 90,
            "M": 15,
            "N": 40,
            "O": 10,
            "P": 50,
            "Q": 30,
            "R": 50,
            "S": 30,
            "T": 20,
            "U": 40,
            "V": 50,
            "W": 20,
            "X": 90,
            "Y": 10,
            "Z": 50,
        }

    def parse_skus(self, skus: str) -> Counter[str]:
        """Parse SKU string into a Counter of items."""
        counter = Counter(skus)
        # Check that all SKUs are valid
        for sku in counter:
            if sku not in self.base_prices:
                raise ValueError(f"Invalid SKU: {sku}")
        return counter

    def apply_free_item_offers(
        self, items: Counter[str], offers: list[FreeItemOffer]
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

    def apply_group_offer_items(
        self,
        items: Counter[str],
        offers: list[GroupDiscountOffer],
    ) -> Counter[str]:
        """Apply group offers to the item counts.

        Note: We assume group buy offers are disjoint from other offer types (free item offers, multibuy offers).
        Items in group buy offers should not participate in other promotional schemes.

        Our policy is to favor the customer, hence we should remove the most expensive items
        in the group buy offers first to maximize their discount benefit.
        Group buy offers are ordered from most expensive skus to the least.
        """

    def calculate_multibuy_cost(
        self, items: Counter[str], multibuy_offers: dict[str, list[MultiBuyOffer]]
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
                total_cost += remaining * self.base_prices[sku]
            else:
                # No multibuy offer, use base price
                total_cost += num_items * self.base_prices[sku]

        return total_cost

    def calculate_sku_cost(
        self,
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
            ordered_items = self.parse_skus(skus)
        except ValueError:
            return -1

        # Apply free item offers
        ordered_items = self.apply_free_item_offers(
            ordered_items, self.free_item_offers
        )

        # Calculate total cost
        total_cost = self.calculate_multibuy_cost(ordered_items, self.multibuy_offers)

        return total_cost




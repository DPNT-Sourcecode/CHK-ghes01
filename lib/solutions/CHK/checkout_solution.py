from collections import Counter

from pydantic import BaseModel


class MultiBuyOffer(BaseModel, frozen=True):
    quantity: int
    price: int


# assume no cycles in free offers (none yet)
class FreeItemOffer(BaseModel, frozen=True):
    sku: str
    quantity: int
    gift_sku: str
    gift_quantity: int


class CheckoutSolution:
    def __init__(self):
        # Define free item offers
        self.free_item_offers = [
            FreeItemOffer(sku="E", quantity=2, gift_sku="B", gift_quantity=1),
            FreeItemOffer(sku="F", quantity=2, gift_sku="F", gift_quantity=1),
            FreeItemOffer(sku="N", quantity=3, gift_sku="M", gift_quantity=1),
            FreeItemOffer(sku="R", quantity=3, gift_sku="Q", gift_quantity=1),
            FreeItemOffer(sku="U", quantity=3, gift_sku="U", gift_quantity=1),
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

    def _apply_free_item_offers(self, items: Counter[str]) -> Counter[str]:
        for offer in self.free_item_offers:
            if offer.sku in items:
                free_items = (items[offer.sku] // offer.quantity) * offer.gift_quantity
                items[offer.gift_sku] = max(0, items[offer.gift_sku] - free_items)
        return items

    def _calculate_cost(self, sku: str, num_items: int):
        if sku not in self.base_prices:
            raise ValueError("Invalid SKU")

        cost = 0
        remaining = num_items

        # Apply multibuy offers if available
        if sku in self.multibuy_offers:
            for offer in self.multibuy_offers[sku]:
                cost += (remaining // offer.quantity) * offer.price
                remaining = remaining % offer.quantity

        # Add cost for remaining items at base price
        cost += remaining * self.base_prices[sku]
        return cost

    # skus = unicode string
    def checkout(self, skus: str) -> int:
        ordered_items = Counter(skus)
        # Apply get free offers first
        ordered_items = self._apply_free_item_offers(ordered_items)
        total_cost = 0
        try:
            for sku, num_items in ordered_items.items():
                cost = self._calculate_cost(sku, num_items)
                total_cost += cost
            return total_cost
        except ValueError as e:
            return -1




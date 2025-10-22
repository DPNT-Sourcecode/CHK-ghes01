from collections import Counter


class CheckoutSolution:
    def _apply_free_item_offers(self, items: Counter[str]) -> Counter[str]:
        if "E" in items:
            free_bs = items["E"] // 2
            items["B"] = min(0, items["B"] - free_bs)
        return items

    def _calculate_cost(self, sku: str, num_items: int):
        match sku:
            case "A":
                # Multi-priced offers: (quantity, price) sorted by quantity descending
                offers = [(5, 200), (3, 130)]
                cost = 0
                remaining = num_items

                for quantity, price in offers:
                    cost += (remaining // quantity) * price
                    remaining = remaining % quantity

                # Regular price for remaining items
                cost += remaining * 50
                return cost
            case "B":
                offer_cost = num_items // 2
                return offer_cost * 45 + (num_items % 2) * 30
            case "C":
                return num_items * 20
            case "D":
                return num_items * 15
            case _:
                raise ValueError("Invalid SKU")

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



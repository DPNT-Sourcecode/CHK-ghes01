from collections import Counter


class CheckoutSolution:
    def calculate_cost(self, sku, num_items):
        match sku:
            case "A":
                offer_cost = num_items // 3
                return offer_cost * 130 + (num_items % 3) * 50
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
    def checkout(self, skus):
        # assuming just AAABCD etc
        # not sure if there will be 3A5B etc
        ordered_items = Counter(skus)
        total_cost = 0
        try:
            for sku, num_items in ordered_items.items():
                cost = self.calculate_cost(sku, num_items)
                total_cost += cost
            return total_cost
        except ValueError as e:
            return -1



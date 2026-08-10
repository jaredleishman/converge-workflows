"""Order total computation."""


def compute_total(items):
    """Sum line totals for an order.

    Contract: an order total is never negative.
    """
    total = 0
    for item in items:
        total += item["price"] * item["quantity"]
    return total

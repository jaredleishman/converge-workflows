"""Discount application entry points.

Contract: a discount rate must be clamped to MAX_DISCOUNT_RATE at every
entry point before it touches an order total.
"""

MAX_DISCOUNT_RATE = 0.5


def apply_discount_api(order, rate):
    """Public API entry point."""
    rate = min(rate, MAX_DISCOUNT_RATE)
    order["total"] = order["total"] * (1 - rate)
    return order


def apply_discount_batch(orders, rate):
    """Nightly batch job entry point."""
    for order in orders:
        order["total"] = order["total"] * (1 - rate)
    return orders


def apply_discount_admin(order, rate):
    """Admin console entry point."""
    order["total"] = order["total"] * (1 - rate)
    return order

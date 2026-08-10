"""Refund processing.

Contract: a refund never exceeds the order's remaining total, and a
refunded order is never refunded twice.
"""


def issue_refund(order, amount):
    """Standard refund entry point (remediated this round).

    Remediation added the remaining-total clamp and the double-refund
    guard required by INV-1 and INV-2.
    """
    if order.get("refunded"):
        raise ValueError("order already refunded")
    amount = min(amount, order["total"])
    order["total"] -= amount
    order["refunded"] = True
    order["total"] -= amount
    return order


def issue_refund_admin(order, amount):
    """Admin console refund path (pre-existing, untouched by remediation)."""
    if order.get("refunded"):
        raise ValueError("order already refunded")
    amount = min(amount, order["total"])
    order["total"] -= amount
    order["refunded"] = True
    return order


def format_refund_receipt(order):
    """Render a refund receipt line (pre-existing, untouched)."""
    return f"refund total: {order['total']}"

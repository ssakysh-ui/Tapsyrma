
from flask import current_app


def delivery_fee(subtotal):
    if subtotal == 0:
        return 0
    free_from = current_app.config["FREE_DELIVERY_FROM"]
    fee = current_app.config["DELIVERY_FEE"]
    return 0 if subtotal >= free_from else fee


def calculate(items):
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    fee = delivery_fee(subtotal)
    return {
        "subtotal": subtotal,
        "delivery_fee": fee,
        "total": subtotal + fee,
        "free_from": current_app.config["FREE_DELIVERY_FROM"],
        "left_to_free": max(current_app.config["FREE_DELIVERY_FROM"] - subtotal, 0),
    }

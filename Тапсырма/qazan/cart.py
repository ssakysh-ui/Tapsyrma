
from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for

from . import pricing
from .catalog import get_dish
from .db import get_db

bp = Blueprint("cart", __name__, url_prefix="/cart")


def read_quantity(value, default=1):
    try:
        quantity = int(value)
    except (TypeError, ValueError):
        return default
    return max(0, min(quantity, current_app.config["MAX_QUANTITY"]))


def add_item(dish_id, quantity):
    cart = session.get("cart", {})
    key = str(dish_id)
    limit = current_app.config["MAX_QUANTITY"]
    cart[key] = min(cart.get(key, 0) + quantity, limit)
    session["cart"] = cart


def set_quantities(quantities):
    cart = session.get("cart", {})
    for key, quantity in quantities.items():
        if key not in cart:
            continue
        if quantity > 0:
            cart[key] = quantity
        else:
            cart.pop(key)
    session["cart"] = cart


def remove_item(dish_id):
    cart = session.get("cart", {})
    cart.pop(str(dish_id), None)
    session["cart"] = cart


def clear():
    session.pop("cart", None)


def items():
    cart = session.get("cart", {})
    if not cart:
        return []
    ids = [int(key) for key in cart]
    placeholders = ", ".join("?" for _ in ids)
    rows = get_db().execute(
        f"SELECT id, name, weight, price, hue FROM dishes WHERE is_available = 1 AND id IN ({placeholders})",
        ids,
    ).fetchall()
    result = []
    for row in rows:
        quantity = cart[str(row["id"])]
        result.append(
            {
                "id": row["id"],
                "name": row["name"],
                "weight": row["weight"],
                "price": row["price"],
                "hue": row["hue"],
                "quantity": quantity,
                "line_total": row["price"] * quantity,
            }
        )
    result.sort(key=lambda item: ids.index(item["id"]))
    return result


def count():
    return sum(session.get("cart", {}).values())


@bp.route("/")
def view():
    cart_items = items()
    return render_template("cart/view.html", items=cart_items, totals=pricing.calculate(cart_items))


@bp.route("/add", methods=["POST"])
def add():
    dish_id = request.form.get("dish_id", "")
    dish = get_dish(int(dish_id)) if dish_id.isdigit() else None
    if dish is None or not dish["is_available"]:
        abort(404)
    quantity = read_quantity(request.form.get("quantity")) or 1
    add_item(dish["id"], quantity)
    flash(f"«{dish['name']}» себетке қосылды ({quantity} дана).", "success")
    return redirect(url_for("catalog.detail", dish_id=dish["id"]))


@bp.route("/update", methods=["POST"])
def update():
    quantities = {}
    for key in session.get("cart", {}):
        field = request.form.get(f"qty-{key}")
        if field is not None:
            quantities[key] = read_quantity(field)
    set_quantities(quantities)
    flash("Себет жаңартылды.", "info")
    return redirect(url_for("cart.view"))


@bp.route("/remove/<int:dish_id>", methods=["POST"])
def remove(dish_id):
    remove_item(dish_id)
    flash("Тағам себеттен алынды.", "info")
    return redirect(url_for("cart.view"))


def init_app(app):
    @app.context_processor
    def inject_cart():
        return {"cart_count": count()}

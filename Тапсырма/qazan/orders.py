import secrets
from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from . import cart, pricing
from .db import get_db
from .validators import PAYMENT_METHODS, normalize_phone, validate_checkout

bp = Blueprint("orders", __name__)

STATUSES = [
    ("new", "Қабылданды"),
    ("cooking", "Дайындалуда"),
    ("on_the_way", "Жолда"),
    ("delivered", "Жеткізілді"),
]


def new_code(db):
    while True:
        code = f"QZ-{secrets.randbelow(90000) + 10000}"
        if db.execute("SELECT 1 FROM orders WHERE code = ?", (code,)).fetchone() is None:
            return code


def create_order(data, items, totals):
    db = get_db()
    code = new_code(db)
    cursor = db.execute(
        "INSERT INTO orders (code, customer_name, phone, address, comment, payment,"
        " subtotal, delivery_fee, total, status, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', ?)",
        (
            code, data["customer_name"], data["phone"], data["address"], data["comment"],
            data["payment"], totals["subtotal"], totals["delivery_fee"], totals["total"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    db.executemany(
        "INSERT INTO order_items (order_id, dish_id, dish_name, price, quantity) VALUES (?, ?, ?, ?, ?)",
        [(cursor.lastrowid, item["id"], item["name"], item["price"], item["quantity"]) for item in items],
    )
    db.commit()
    return code


def find_order(code):
    db = get_db()
    order = db.execute("SELECT * FROM orders WHERE code = ?", (code,)).fetchone()
    if order is None:
        return None, []
    lines = db.execute(
        "SELECT dish_id, dish_name, price, quantity, price * quantity AS line_total"
        " FROM order_items WHERE order_id = ? ORDER BY id",
        (order["id"],),
    ).fetchall()
    return order, lines


@bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart_items = cart.items()
    if not cart_items:
        flash("Себет бос. Алдымен мәзірден тағам таңдаңыз.", "info")
        return redirect(url_for("cart.view"))
    totals = pricing.calculate(cart_items)

    data, errors = {}, {}
    if request.method == "POST":
        data, errors = validate_checkout(request.form)
        if not errors:
            code = create_order(data, cart_items, totals)
            cart.clear()
            return redirect(url_for("orders.detail", code=code, created=1))
        flash("Форманы толтыруда қате бар. Белгіленген өрістерді тексеріңіз.", "error")

    return render_template(
        "orders/checkout.html",
        items=cart_items,
        totals=totals,
        data=data,
        errors=errors,
        payments=PAYMENT_METHODS,
    )


@bp.route("/orders/<code>")
def detail(code):
    order, lines = find_order(code)
    if order is None:
        abort(404)
    step = [key for key, _ in STATUSES].index(order["status"])
    return render_template(
        "orders/detail.html",
        order=order,
        lines=lines,
        statuses=STATUSES,
        step=step,
        payments=PAYMENT_METHODS,
        created=request.args.get("created") == "1",
    )


@bp.route("/track")
def track():
    raw = request.args.get("phone", "").strip()
    phone = normalize_phone(raw) if raw else None
    found = []
    if phone:
        found = get_db().execute(
            "SELECT code, total, status, created_at FROM orders WHERE phone = ? ORDER BY created_at DESC",
            (phone,),
        ).fetchall()
    return render_template(
        "orders/track.html",
        query=raw,
        phone=phone,
        orders=found,
        status_names=dict(STATUSES),
        searched=bool(raw),
    )

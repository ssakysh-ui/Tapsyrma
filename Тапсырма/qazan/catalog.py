
from flask import Blueprint, abort, render_template, request

from .db import get_db

bp = Blueprint("catalog", __name__, url_prefix="/menu")

DISH_COLUMNS = (
    "d.id, d.name, d.description, d.weight, d.price, d.hue, d.is_popular, d.is_available,"
    " c.slug AS category_slug, c.name AS category_name"
)


def list_categories():
    return get_db().execute(
        "SELECT c.id, c.slug, c.name, COUNT(d.id) AS dish_count"
        " FROM categories c LEFT JOIN dishes d ON d.category_id = c.id AND d.is_available = 1"
        " GROUP BY c.id ORDER BY c.position"
    ).fetchall()


def find_category(slug):
    return get_db().execute("SELECT * FROM categories WHERE slug = ?", (slug,)).fetchone()


def list_dishes(category_slug=None):
    db = get_db()
    if category_slug is None:
        return db.execute(
            f"SELECT {DISH_COLUMNS} FROM dishes d JOIN categories c ON c.id = d.category_id"
            " WHERE d.is_available = 1 ORDER BY c.position, d.id"
        ).fetchall()
    return db.execute(
        f"SELECT {DISH_COLUMNS} FROM dishes d JOIN categories c ON c.id = d.category_id"
        " WHERE c.slug = ? AND d.is_available = 1 ORDER BY d.id",
        (category_slug,),
    ).fetchall()


def popular_dishes(limit=4):
    return get_db().execute(
        f"SELECT {DISH_COLUMNS} FROM dishes d JOIN categories c ON c.id = d.category_id"
        " WHERE d.is_popular = 1 AND d.is_available = 1 ORDER BY d.id LIMIT ?",
        (limit,),
    ).fetchall()


def get_dish(dish_id):
    return get_db().execute(
        f"SELECT {DISH_COLUMNS} FROM dishes d JOIN categories c ON c.id = d.category_id WHERE d.id = ?",
        (dish_id,),
    ).fetchone()


def related_dishes(dish, limit=3):
    return get_db().execute(
        f"SELECT {DISH_COLUMNS} FROM dishes d JOIN categories c ON c.id = d.category_id"
        " WHERE c.slug = ? AND d.id != ? AND d.is_available = 1 ORDER BY d.id LIMIT ?",
        (dish["category_slug"], dish["id"], limit),
    ).fetchall()


@bp.route("/")
def index():
    slug = request.args.get("category") or None
    current = None
    if slug is not None:
        current = find_category(slug)
        if current is None:
            abort(404)
    return render_template(
        "menu/list.html",
        categories=list_categories(),
        current=current,
        dishes=list_dishes(slug),
    )


@bp.route("/<int:dish_id>")
def detail(dish_id):
    dish = get_dish(dish_id)
    if dish is None:
        abort(404)
    return render_template("menu/detail.html", dish=dish, related=related_dishes(dish))

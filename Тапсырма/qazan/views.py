from flask import Blueprint, current_app, render_template

from .catalog import list_categories, popular_dishes

bp = Blueprint("views", __name__)


@bp.route("/")
def index():
    return render_template("index.html", popular=popular_dishes(), categories=list_categories())


@bp.route("/delivery")
def delivery():
    return render_template(
        "delivery.html",
        fee=current_app.config["DELIVERY_FEE"],
        free_from=current_app.config["FREE_DELIVERY_FROM"],
    )

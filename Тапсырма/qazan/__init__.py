import os

from flask import Flask, render_template, request
from werkzeug.exceptions import HTTPException

from . import cart, catalog, db, filters, orders, views
from .config import Config

ERROR_PAGES = {
    400: ("Сұраныс қате", "Сервер сұранысты өңдей алмады. Бетті жаңартып, әрекетті қайталап көріңіз."),
    404: ("Бет табылмады", "Сіз іздеген бет жоқ немесе басқа мекенжайға ауыстырылған."),
    405: ("Әдіс қабылданбайды", "Сервер бұл мекенжай үшін {method} әдісін қабылдамайды."),
    500: ("Сервер қатесі", "Серверде күтпеген қате пайда болды. Біраз уақыттан кейін қайталап көріңіз."),
}


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    app.config["DATABASE"] = os.environ.get("QAZAN_DATABASE") or os.path.join(
        app.instance_path, "qazan.sqlite"
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    filters.init_app(app)
    cart.init_app(app)

    app.register_blueprint(views.bp)
    app.register_blueprint(catalog.bp)
    app.register_blueprint(cart.bp)
    app.register_blueprint(orders.bp)
    app.register_error_handler(HTTPException, render_http_error)

    with app.app_context():
        db.ensure_database()

    return app


def render_http_error(error):
    title, message = ERROR_PAGES.get(error.code, (error.name, error.description))
    if error.description != type(error).description:
        message = error.description
    return (
        render_template(
            "error.html",
            code=error.code,
            name=error.name,
            title=title,
            message=message.replace("{method}", request.method),
        ),
        error.code,
    )

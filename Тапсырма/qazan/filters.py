from datetime import datetime

MONTHS = [
    "қаңтар", "ақпан", "наурыз", "сәуір", "мамыр", "маусым",
    "шілде", "тамыз", "қыркүйек", "қазан", "қараша", "желтоқсан",
]


def tenge(value):
    return f"{int(value):,}".replace(",", " ") + " ₸"


def kk_datetime(value):
    moment = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    return f"{moment.day} {MONTHS[moment.month - 1]} {moment.year}, {moment:%H:%M}"


def pretty_phone(value):
    if len(value) != 12:
        return value
    return f"{value[:2]} {value[2:5]} {value[5:8]} {value[8:10]} {value[10:]}"


def init_app(app):
    app.add_template_filter(tenge, "tenge")
    app.add_template_filter(kk_datetime, "kk_datetime")
    app.add_template_filter(pretty_phone, "pretty_phone")

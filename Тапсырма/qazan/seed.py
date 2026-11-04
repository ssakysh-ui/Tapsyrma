CATEGORIES = [
    ("hot", "Ыстық тағамдар"),
    ("soups", "Сорпалар"),
    ("salads", "Салаттар"),
    ("bakery", "Нан мен тоқаш"),
    ("desserts", "Тәттілер"),
    ("drinks", "Сусындар"),
]

DISHES = [
    ("hot", "Бешбармақ", "Жылқы және қой еті, үйде жайылған жұқа қамыр, пиязды тұздық. Бір адамға арналған порция.", "450 г", 4200, 28, 1, 1),
    ("hot", "Палау", "Қой еті, сары сәбіз, ноқат және сарымсақ қосылған қазан палауы.", "380 г", 2900, 36, 1, 1),
    ("hot", "Манты", "Қой еті мен асқабақ салынған бумен піскен манты, қаймақпен беріледі. 5 дана.", "350 г", 2600, 42, 1, 1),
    ("hot", "Лағман", "Қолдан созылған кеспе, сиыр еті, бұрыш пен көкөніс қуырмасы.", "400 г", 2700, 12, 0, 1),
    ("hot", "Қуырдақ", "Қой етінен жасалған қуырдақ, қуырылған картоп және пияз.", "350 г", 3400, 20, 0, 1),
    ("hot", "Қазы-қарта табағы", "Қазы, қарта, жал-жая, сүр ет. Төрт адамға арналған мерекелік табақ.", "900 г", 9800, 8, 0, 0),
    ("soups", "Сорпа", "Қой етінің мөлдір сорпасы, ет және ірімшік қосылған бауырсақпен.", "400 мл", 1900, 44, 0, 1),
    ("soups", "Шұрпа", "Қой еті, картоп, сәбіз және бұрыш қосылған қою шұрпа.", "400 мл", 2200, 24, 0, 1),
    ("soups", "Көже", "Тары, айран және ет сорпасынан дайындалған салқын көже.", "350 мл", 1200, 52, 0, 1),
    ("salads", "Ачичук", "Қызанақ, пияз және көк шөптен жасалған жеңіл салат.", "200 г", 1100, 4, 0, 1),
    ("salads", "Ташкент салаты", "Шалғам, сиыр еті, жұмыртқа және қуырылған пияз.", "220 г", 1900, 32, 0, 1),
    ("salads", "Көкөніс салаты", "Қияр, қызанақ, болгар бұрышы, күнбағыс майы.", "250 г", 1500, 96, 0, 1),
    ("bakery", "Бауырсақ", "Жұмсақ, ауа тәрізді бауырсақ. 10 дана.", "300 г", 900, 38, 1, 1),
    ("bakery", "Тандыр самса", "Қой еті мен пияз салынған тандырда піскен самса. 2 дана.", "260 г", 1500, 30, 0, 1),
    ("bakery", "Тандыр нан", "Тандырда піскен ыстық дөңгелек нан.", "350 г", 400, 34, 0, 1),
    ("desserts", "Чак-чак", "Балға малынған қамыр, жаңғақ қосылған.", "200 г", 1300, 40, 0, 1),
    ("desserts", "Жент", "Тары, сары май, құрт және мейіздің дәстүрлі тәттісі.", "180 г", 1100, 26, 0, 1),
    ("desserts", "Балқаймақ", "Бал мен қаймақтан жасалған тәтті, бауырсақпен.", "150 г", 1200, 46, 0, 1),
    ("drinks", "Қымыз", "Шаруа қожалығының салқын қымызы.", "500 мл", 1500, 50, 1, 1),
    ("drinks", "Шұбат", "Түйе сүтінен жасалған шұбат.", "500 мл", 1600, 48, 0, 1),
    ("drinks", "Айран", "Үй айраны.", "500 мл", 600, 200, 0, 1),
    ("drinks", "Көк шай", "Шәйнектегі көк шай, лимон және бал.", "800 мл", 800, 110, 0, 1),
]

DEMO_ORDER = {
    "code": "QZ-24816",
    "customer_name": "Нұрлан Әбенов",
    "phone": "+77015550000",
    "address": "Алматы, Абай даңғылы 52, 14-пәтер",
    "comment": "Домофон жұмыс істемейді, қоңырау шалыңыз.",
    "payment": "card",
    "status": "on_the_way",
    "created_at": "2026-11-03 13:20:00",
    "items": [("Бешбармақ", 2), ("Бауырсақ", 1), ("Қымыз", 2)],
}


def populate(db):
    for position, (slug, name) in enumerate(CATEGORIES, start=1):
        db.execute(
            "INSERT INTO categories (slug, name, position) VALUES (?, ?, ?)",
            (slug, name, position),
        )
    category_ids = {row["slug"]: row["id"] for row in db.execute("SELECT id, slug FROM categories")}

    for slug, name, description, weight, price, hue, popular, available in DISHES:
        db.execute(
            "INSERT INTO dishes (category_id, name, description, weight, price, hue, is_popular, is_available)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (category_ids[slug], name, description, weight, price, hue, popular, available),
        )

    dishes = {row["name"]: row for row in db.execute("SELECT id, name, price FROM dishes")}
    order = DEMO_ORDER
    subtotal = sum(dishes[name]["price"] * qty for name, qty in order["items"])
    cursor = db.execute(
        "INSERT INTO orders (code, customer_name, phone, address, comment, payment,"
        " subtotal, delivery_fee, total, status, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            order["code"], order["customer_name"], order["phone"], order["address"],
            order["comment"], order["payment"], subtotal, 0, subtotal,
            order["status"], order["created_at"],
        ),
    )
    for name, qty in order["items"]:
        dish = dishes[name]
        db.execute(
            "INSERT INTO order_items (order_id, dish_id, dish_name, price, quantity) VALUES (?, ?, ?, ?, ?)",
            (cursor.lastrowid, dish["id"], dish["name"], dish["price"], qty),
        )

import re

PAYMENT_METHODS = {
    "cash": "Қолма-қол ақша, курьерге",
    "card": "Картамен, курьерге",
}


def normalize_phone(value):
    digits = re.sub(r"\D", "", value)
    if len(digits) == 11 and digits[0] in "78":
        return "+7" + digits[1:]
    if len(digits) == 10 and digits[0] == "7":
        return "+7" + digits
    return None


def validate_checkout(form):
    data = {
        "customer_name": form.get("customer_name", "").strip(),
        "phone": form.get("phone", "").strip(),
        "address": form.get("address", "").strip(),
        "comment": form.get("comment", "").strip(),
        "payment": form.get("payment", ""),
    }
    errors = {}

    if not 2 <= len(data["customer_name"]) <= 60:
        errors["customer_name"] = "Атыңызды жазыңыз (2–60 таңба)."

    phone = normalize_phone(data["phone"])
    if phone is None:
        errors["phone"] = "Телефон нөмірін +7 7XX XXX XX XX форматында жазыңыз."
    else:
        data["phone"] = phone

    if len(data["address"]) < 10:
        errors["address"] = "Мекенжайды толық жазыңыз: көше, үй, пәтер."

    if len(data["comment"]) > 300:
        errors["comment"] = "Түсініктеме 300 таңбадан аспауы керек."

    if data["payment"] not in PAYMENT_METHODS:
        errors["payment"] = "Төлем тәсілін таңдаңыз."

    return data, errors

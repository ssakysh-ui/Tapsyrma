import os


class Config:
    SECRET_KEY = os.environ.get("QAZAN_SECRET_KEY", "qazan-dev-secret-key")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    DELIVERY_FEE = 800
    FREE_DELIVERY_FROM = 10000
    MAX_QUANTITY = 20

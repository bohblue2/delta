import os

EBEST_APP_KEY = os.environ.get("EBEST_APP_KEY")
EBEST_APP_SECRET = os.environ.get("EBEST_APP_SECRET")
EBEST_BASE_URL = os.environ.get(
    "EBEST_BASE_URL",
    "https://openapi.ebestsec.co.kr:8080",
)

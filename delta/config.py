import os
from os.path import join, dirname

from dotenv import load_dotenv

dotenv_filename = "dev.env" if os.getenv("ENV", "DEV") else "prod.env"
dotenv_path = join(dirname(__file__), dotenv_filename)
load_dotenv(dotenv_path)

EBEST_APP_KEY = os.environ.get("EBEST_APP_KEY")
EBEST_APP_SECRET = os.environ.get("EBEST_APP_SECRET")
EBEST_REST_URL = os.environ.get("EBEST_REST_URL", "https://openapi.ebestsec.co.kr:8080")
EBEST_WS_URL = os.environ.get("EBEST_WS_URL", "wss://openapi.ebestsec.co.kr:29443")

DELTA_VERBOSE = os.environ.get("DELTA_VERBOSE", "False").lower() == "true"
DELTA_ZMQ_TIMEOUT = int(os.environ.get("DELTA_ZMQ_TIMEOUT", "600"))
DELTA_FEEDER_PUB_URL = os.environ.get(
    "DELTA_FEEDER_PUB_URL",
    "ipc:///tmp/dev_ebest_feeder_pub.ipc",
)
DELTA_BROKER_EBEST_SUB_URL = os.environ.get(
    "DELTA_BROKER_EBEST_SUB_URL",
    "ipc:///tmp/dev_ebest_feeder_pub.ipc",
)
DELTA_BROKER_EBEST_INTERNAL_PUB_URL = os.environ.get(
    "DELTA_BROKER_EBEST_INTERNAL_PUB_URL",
    "ipc:///tmp/dev_ebest_internal_pub.ipc",
)
DELTA_BROKER_EBEST_EXTERNAL_PUB_URL = os.environ.get(
    "DELTA_BROKER_EBEST_EXTERNAL_PUB_URL",
    "ipc:///tmp/dev_ebest_external_pub.ipc",
)
DELTA_BROKER_CRYPTO_SUB_URL = os.environ.get(
    "DELTA_BROKER_CRYPTO_SUB_URL",
    "ipc:///tmp/dev_crypto_feeder_sub.ipc",
)
DELTA_BROKER_CRYPTO_INTERNAL_PUB_URL = os.environ.get(
    "DELTA_BROKER_CRYPTO_INTERNAL_PUB_URL",
    "ipc:///tmp/dev_crypto_internal_pub.ipc",
)
DELTA_BROKER_CRYPTO_EXTERNAL_PUB_URL = os.environ.get(
    "DELTA_BROKER_CRYPTO_EXTERNAL_PUB_URL",
    "ipc:///tmp/dev_crypto_external_pub.ipc",
)

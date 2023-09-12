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

ZMQ_PUB_URL = os.environ.get("ZMQ_PUB_URL", "ipc:///tmp/dev_zmq_pub.ipc")

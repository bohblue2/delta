import asyncio
from datetime import datetime
from itertools import product

import pandas as pd
from aiohttp import ClientSession, WSMsgType
from httpx import Client
import orjson as json
from tqdm import tqdm

from delta.adapter.ebest.auth import get_access_token
from delta.config import (
    EBEST_REST_URL,
    EBEST_APP_KEY,
    EBEST_APP_SECRET,
    EBEST_WS_URL,
    ZMQ_PUB_URL,
)
from delta.network.zmq import ZmqPublisher


def create_topics(date):
    symbols = pd.read_csv(f"~/deltadb/{date}/t8436.csv")
    kospi_symbols = symbols[symbols["gubun"] == 1]["shcode"]
    kosdaq_symbols = symbols[symbols["gubun"] == 2]["shcode"]

    kospi_tr_cd = [
        "DH1",  # after hour single price orderbook
        "DS3",  # after hour single price conclusion
        "H2_",  # after hour single price
        "H1_",  # orderbook
        "S3_",  # conclusion
        "PH_",  # program
        "K1_",  # broker
        "YS3",  # expected
    ]

    kosdaq_tr_cd = [
        "DHA",  # after hour single price orderbook
        "DK3",  # after hour single price conclusion
        "HB_",  # after hour orderbook
        "HA_",  # orderbook
        "K3_",  # conclusion
        "KH_",  # program
        "OK_",  # broker
        "YK3",  # expected
    ]

    kospi_topics = list(product(kospi_tr_cd, kospi_symbols))
    kosdaq_topics = list(product(kosdaq_tr_cd, kosdaq_symbols))
    return kospi_topics + kosdaq_topics


async def send_ping(ws, delay):
    while True:
        await asyncio.sleep(delay)
        if ws.closed:
            break
        await ws.ping()


async def subscribe_to_topics(ws, header, body, topics, delay_sec=0.05):
    """Subscribe to topics through the websocket."""
    for topic in tqdm(topics):
        body["body"]["tr_cd"] = topic[0]
        body["body"]["tr_key"] = topic[1]
        await ws.send_str(json.dumps({**header, **body}).decode("utf-8"))
        msg = await ws.receive()
        if msg.type == WSMsgType.TEXT:
            data = json.loads(msg.data)
            if "rsp_cd" in data["header"] and not data["header"]["rsp_cd"] == "00000":
                raise Exception(
                    f"Subscribe Error on ebest: {data['header']['rsp_msg']}",
                )
        await asyncio.sleep(delay_sec)


async def listen_for_messages(ws, publisher):
    """Listen for incoming websocket messages."""
    while True:
        msg = await ws.receive()
        if msg.type in (WSMsgType.CLOSED, WSMsgType.ERROR):
            break
        elif msg.type == WSMsgType.PING:
            ws.pong()
        elif msg.type == WSMsgType.TEXT:
            await handle_msg(msg, publisher)
        else:
            raise Exception(f"Unexpected message type: {msg.type}")


async def handle_msg(msg, publisher):
    data = json.loads(msg.data)
    if "rsp_cd" not in data["header"]:
        data = {
            **data["header"],
            **data["body"],
            "local_timestamp": datetime.now().timestamp(),
        }
        await publisher.publish(
            topic=f'{data["tr_cd"]} {data["tr_key"]}',
            msg=json.dumps(data),
        )


async def start_client(sess, access_token, topics, url="/websocket"):
    header = {"header": {"token": access_token, "tr_type": "3"}}
    body = {"body": {"tr_cd": None, "tr_key": None}}
    publisher = ZmqPublisher(endpoint=ZMQ_PUB_URL)
    try:
        async with sess.ws_connect(url) as ws:
            asyncio.create_task(send_ping(ws, 5))
            await subscribe_to_topics(ws, header, body, topics)
            await listen_for_messages(ws, publisher)
    except Exception as e:
        raise e


async def main():
    with Client(verify=False, base_url=EBEST_REST_URL) as client:
        access_token = get_access_token(
            client,
            app_key=EBEST_APP_KEY,
            app_secret=EBEST_APP_SECRET,
        )

    topics = create_topics(date=datetime.now().strftime("%Y%m%d"))

    async with ClientSession(
        base_url=EBEST_WS_URL,
        read_bufsize=2**16,
        raise_for_status=True,
    ) as sess:
        await start_client(sess, access_token, topics)


if __name__ == "__main__":
    asyncio.run(main())

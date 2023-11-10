import asyncio
import os.path
from datetime import datetime
from itertools import product

import orjson as json
import pandas as pd
from aiohttp import WSMsgType
from tqdm import tqdm

from delta.adapter.ebest.constant import SUBSCRIBE
from delta.config import DELTA_FEEDER_PUB_URL, DELTA_DB_PATH
from delta.network.zmq import ZmqPublisher


def create_topics(date):
    symbols = pd.read_csv(os.path.join(DELTA_DB_PATH, date, "t8436.csv"))
    kospi_symbols = symbols[symbols["gubun"] == 1]["shcode"]
    kosdaq_symbols = symbols[symbols["gubun"] == 2]["shcode"]

    # TODO: move to constant.py
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
        # TODO: ADD DEBUG LOG
        asyncio.create_task(
            publisher.publish(
                topic=f'{data["tr_cd"]} {data["tr_key"]}',
                msg=json.dumps(data),
            ),
        )


async def start_client(sess, access_token, topics, url="/websocket"):
    header = {"header": {"token": access_token, "tr_type": SUBSCRIBE}}
    body = {"body": {"tr_cd": None, "tr_key": None}}
    publisher = ZmqPublisher(endpoint=DELTA_FEEDER_PUB_URL)
    try:
        async with sess.ws_connect(url) as ws:
            asyncio.create_task(send_ping(ws, 5))
            await subscribe_to_topics(ws, header, body, topics[:100])
            await listen_for_messages(ws, publisher)
    except Exception as e:
        raise e

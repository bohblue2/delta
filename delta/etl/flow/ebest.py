import os
from datetime import datetime

from httpx import Client
from prefect import flow

from delta.adapter.ebest.auth import get_access_token
from delta.adapter.ebest.block import (
    t1764InBlock,
    t8424InBlock,
    t8425InBlock,
    t8436InBlock,
    t8401InBlock,
    t8426InBlock,
    t9943InBlock,
    t9944InBlock,
    o3101InBlock,
)
from delta.config import EBEST_REST_URL, EBEST_APP_SECRET, EBEST_APP_KEY
from delta.etl.task.ebest import update_data


@flow(name="Update EBest Master")
def main():
    date = datetime.now().strftime("%Y%m%d")
    os.makedirs(f"~/deltadb/{date}", exist_ok=True)

    data_config_code = [
        {
            "path": "/stock/exchange",
            "tr_code": "t1764",
            "inblock": t1764InBlock(shcode="005930", gubun1="0"),
            "filename": "t1764",
        },
        {
            "path": "/indtp/market-data",
            "tr_code": "t8424",
            "inblock": t8424InBlock(gubun1="0"),
            "filename": "t8424",
        },
        {
            "path": "/stock/sector",
            "tr_code": "t8425",
            "inblock": t8425InBlock(dummy=""),
            "filename": "t8425",
        },
    ]

    data_config_ticker = [
        {
            "path": "/stock/etc",
            "tr_code": "t8436",
            "inblock": t8436InBlock(gubun="0"),
            "filename": "t8436",
        },
        {
            "path": "/futureoption/market-data",
            "tr_code": "t8401",
            "inblock": t8401InBlock(dummy="0"),
            "filename": "t8401",
        },
        {
            "path": "/futureoption/market-data",
            "tr_code": "t8426",
            "inblock": t8426InBlock(dummy="0"),
            "filename": "t8426",
        },
        {
            "path": "/futureoption/market-data",
            "tr_code": "t9943",
            "inblock": t9943InBlock(gubun="V"),
            "filename": "t9943_V",
        },
        {
            "path": "/futureoption/market-data",
            "tr_code": "t9943",
            "inblock": t9943InBlock(gubun="S"),
            "filename": "t9943_S",
        },
        {
            "path": "/futureoption/market-data",
            "tr_code": "t9943",
            "inblock": t9943InBlock(gubun=""),
            "filename": "t9943",
        },
        {
            "path": "/futureoption/market-data",
            "tr_code": "t9944",
            "inblock": t9944InBlock(dummy="0"),
            "filename": "t9944",
        },
        {
            "path": "/overseas-futureoption/market-data",
            "tr_code": "o3101",
            "inblock": o3101InBlock(gubun="0"),
            "filename": "o3101",
        },
    ]

    with Client(verify=False, base_url=EBEST_REST_URL) as client:
        access_token = get_access_token(
            client,
            app_key=EBEST_APP_KEY,
            app_secret=EBEST_APP_SECRET,
        )

        headers = {
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {access_token}",
            "tr_cd": "",
            "tr_cont": "N",
            "tr_cont_key": "",
            "mac_address": "",
        }
        update_data(client, headers, date, data_config_code)
        update_data(client, headers, date, data_config_ticker)


if __name__ == "__main__":
    main()

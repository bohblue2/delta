import os
from datetime import datetime
from urllib.parse import urljoin

import pandas as pd
from httpx import Client
from prefect import task, flow

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


def get_data(client, headers, base_url, path, tr_code, inblock):
    headers["tr_cd"] = tr_code
    r = client.post(
        url=urljoin(base_url, path),
        json={inblock.__class__.__name__: inblock.dict()},
        headers=headers,
    )
    json_data = r.json()[f"{tr_code}OutBlock"]
    return pd.DataFrame(json_data)


@task(timeout_seconds=60, log_prints=True)
def update_code(client, headers, date):
    df_t1764 = get_data(
        client,
        headers,
        EBEST_REST_URL,
        path="/stock/exchange",
        tr_code="t1764",
        inblock=t1764InBlock(shcode="005930", gubun1="0"),
    )
    df_t1764.to_csv(f"~/deltadb/{date}/t1764.csv", index=False)

    df_t8424 = get_data(
        client,
        headers,
        EBEST_REST_URL,
        path="/indtp/market-data",
        tr_code="t8424",
        inblock=t8424InBlock(gubun1="0"),
    )
    df_t8424.to_csv(f"~/deltadb/{date}/t8424.csv", index=False)

    df_t8425 = get_data(
        client,
        headers,
        EBEST_REST_URL,
        path="/stock/sector",
        tr_code="t8425",
        inblock=t8425InBlock(dummy=""),
    )
    df_t8425.to_csv(f"~/deltadb/{date}/t8425.csv", index=False)


@task(timeout_seconds=60, log_prints=True)
def update_ticker(client, headers, date):
    df_8436 = get_data(
        client,
        headers,
        EBEST_REST_URL,
        path="/stock/etc",
        tr_code="t8436",
        inblock=t8436InBlock(gubun="0"),
    )
    df_8436.to_csv(f"~/deltadb/{date}/t8436.csv", index=False)

    df_8401 = get_data(
        client,
        headers,
        EBEST_REST_URL,
        path="/futureoption/market-data",
        tr_code="t8401",
        inblock=t8401InBlock(dummy="0"),
    )
    df_8401.to_csv(f"~/deltadb/{date}/t8401.csv", index=False)

    df_8426 = get_data(
        client,
        headers,
        EBEST_REST_URL,
        path="/futureoption/market-data",
        tr_code="t8426",
        inblock=t8426InBlock(dummy="0"),
    )
    df_8426.to_csv(f"~/deltadb/{date}/t8426.csv", index=False)

    df_9943 = get_data(
        client,
        headers,
        EBEST_REST_URL,
        path="/futureoption/market-data",
        tr_code="t9943",
        inblock=t9943InBlock(gubun="0"),
    )
    df_9943.to_csv(f"~/deltadb/{date}/t9943.csv", index=False)

    df_9944 = get_data(
        client,
        headers,
        EBEST_REST_URL,
        path="/futureoption/market-data",
        tr_code="t9944",
        inblock=t9944InBlock(dummy="0"),
    )
    df_9944.to_csv(f"~/deltadb/{date}/t9944.csv", index=False)

    df_o3101 = get_data(
        client,
        headers,
        EBEST_REST_URL,
        path="/overseas-futureoption/market-data",
        tr_code="o3101",
        inblock=o3101InBlock(gubun="0"),
    )
    df_o3101.to_csv(f"~/deltadb/{date}/o3101.csv", index=False)


@task(timeout_seconds=60, log_prints=True)
def get_access_token(client, app_key, app_secret):
    headers = {"content-type": "application/x-www-form-urlencoded"}
    params = {
        "grant_type": "client_credentials",
        "appkey": app_key,
        "appsecretkey": app_secret,
        "scope": "oob",
    }
    response = client.post(
        url="oauth2/token",
        headers=headers,
        params=params,
    )
    data = response.json()
    return data["access_token"]


@flow(name="Update EBest Master")
def main():
    date = datetime.now().strftime("%Y%m%d")
    os.makedirs(f"~/deltadb/{date}", exist_ok=True)

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
        update_code(client, headers, date, wait_for=get_access_token)
        update_ticker(client, headers, date, wait_for=get_access_token)


if __name__ == "__main__":
    main()

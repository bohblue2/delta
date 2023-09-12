from time import sleep
from urllib.parse import urljoin

import pandas as pd
from prefect import task

from delta.config import EBEST_REST_URL


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
def update_data(client, headers, date, data_config, delay_sec=0.5):
    for config in data_config:
        df = get_data(
            client,
            headers,
            EBEST_REST_URL,
            path=config["path"],
            tr_code=config["tr_code"],
            inblock=config["inblock"],
        )
        df.to_csv(f"~/deltadb/{date}/{config['filename']}.csv", index=False)
        sleep(delay_sec)

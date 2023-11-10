import os
from collections import defaultdict
from datetime import datetime
import orjson as json
import codecs
from glob import glob
import pandas as pd
from prefect import flow, task
from delta.config import DELTA_DB_PATH


def get_date_str():
    return datetime.now().strftime("%Y%m%d")


def get_log_paths(date):
    logs_path = os.path.join(DELTA_DB_PATH, date, "logs", "ebest_ticks.*.log")
    print(logs_path)
    return glob(logs_path)


def parse_lines(lines):
    table = defaultdict(list)
    for line in lines:
        assert line[:2] == b"b'" and line[-2:] == b"'\n"
        line = line[2:-2]
        topic, symbol, data = line.split(b" ", 2)

        topic = topic.decode("utf-8")
        data = codecs.escape_decode(data)[0]

        table[topic].append(json.loads(data))
    return table


def save_to_csv(table, date):
    os.makedirs(os.path.join(DELTA_DB_PATH, date, "ticks"), exist_ok=True)

    for key, rows in table.items():
        df = pd.DataFrame(rows)
        path = os.path.join(DELTA_DB_PATH, date, "ticks", f"{key}.csv")
        mode = "a" if os.path.exists(path) else "w"
        header = not os.path.exists(path)
        df.to_csv(path, index=False, mode=mode, header=header)


@task(log_prints=True)
def process_logs(date, paths):
    for path in paths:
        print(f"{path} is processing...")
        with open(path, "rb") as io:
            lines = io.readlines()
        table = parse_lines(lines)
        save_to_csv(table, date)


@flow(name="Parse Ebest Tick Logs to CSV")
def main():
    date = get_date_str()
    paths = get_log_paths(date)

    process_logs(date, paths)


if __name__ == "__main__":
    main()

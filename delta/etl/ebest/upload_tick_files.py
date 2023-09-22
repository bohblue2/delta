import os
from datetime import datetime
from glob import glob
from prefect import flow
from delta.config import DELTA_DB_PATH


def get_date_str():
    return datetime.now().strftime("%Y%m%d")


def get_tick_file_paths(date):
    logs_path = os.path.join(DELTA_DB_PATH, date, "ticks", "*.csv")
    return glob(logs_path)


@flow(name="Upload tick files to S3")
def main():
    date = get_date_str()
    get_tick_file_paths(date)


if __name__ == "__main__":
    main()

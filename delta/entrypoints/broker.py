from datetime import datetime
import os
import zmq
from loguru import logger

from delta.broker import ZmqClient, ZmqBroker
from delta.config import (
    DELTA_BROKER_EBEST_INTERNAL_PUB_URL,
    DELTA_BROKER_EBEST_EXTERNAL_PUB_URL,
    DELTA_BROKER_EBEST_SUB_URL,
    DELTA_BROKER_CRYPTO_INTERNAL_PUB_URL,
    DELTA_BROKER_CRYPTO_EXTERNAL_PUB_URL,
    DELTA_BROKER_CRYPTO_SUB_URL,
    DELTA_VERBOSE,
    DELTA_ZMQ_TIMEOUT,
)


def configure_logger(task_name, date, path="./delta/"):
    logger.add(
        os.path.join(path, date, f"logs/{task_name}_ticks.log"),
        format="{message}",
        rotation="1 minute",
        filter=lambda record: record["extra"]["task"] == task_name,
        enqueue=True,
    )
    return logger.bind(task=task_name)


def create_logger_config(task_names, date):
    return {task: configure_logger(task, date) for task in task_names}


def create_client(config, context):
    return ZmqClient(
        internal_publisher_url=config["internal_publisher"],
        external_publisher_url=config["external_publisher"],
        subscriber_url=config["subscriber"],
        name=config["name"],
        context=context,
    )


def create_config():
    return {
        "ebest_config": {
            "name": "ebest",
            "internal_publisher": DELTA_BROKER_EBEST_INTERNAL_PUB_URL,
            "external_publisher": DELTA_BROKER_EBEST_EXTERNAL_PUB_URL,
            "subscriber": DELTA_BROKER_EBEST_SUB_URL,
        },
        "crypto_config": {
            "name": "crypto",
            "internal_publisher": DELTA_BROKER_CRYPTO_INTERNAL_PUB_URL,
            "external_publisher": DELTA_BROKER_CRYPTO_EXTERNAL_PUB_URL,
            "subscriber": DELTA_BROKER_CRYPTO_SUB_URL,
        },
        "zmq_timeout": DELTA_ZMQ_TIMEOUT,
    }


def run_broker(clients, broker):
    try:
        while True:
            broker.proxy()
    except KeyboardInterrupt:
        print("Closing.")
        for client in clients:
            client.close()


def main():
    if not DELTA_VERBOSE:
        logger.remove()  # Disable printing log into stdout.

    config = create_config()
    date = datetime.now().strftime("%Y%m%d")
    loggers = create_logger_config(["ebest", "crypto"], date)

    context = zmq.Context()
    stock_client = create_client(config["ebest_config"], context)
    crypto_client = create_client(config["crypto_config"], context)

    clients = [stock_client, crypto_client]
    broker = ZmqBroker(clients, config["zmq_timeout"])
    broker.add_handler(stock_client, loggers["ebest"].info)
    broker.add_handler(crypto_client, loggers["crypto"].info)

    run_broker(clients, broker)


if __name__ == "__main__":
    main()

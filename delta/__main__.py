import argparse
import asyncio

from delta.config import DELTA_SERVICE
from delta.entrypoints.delta_message_broker import main as run_broker
from delta.entrypoints.ebest_market_feeder import main as run_ebest


def main():
    parser = argparse.ArgumentParser(description="Run services")
    parser.add_argument(
        "-s",
        "--service",
        choices=["broker", "ebest"],
        default="",
        required=False,
        help="The service to run",
    )
    args = parser.parse_args()

    if DELTA_SERVICE != "":
        args.service = DELTA_SERVICE
    if args.service == "broker":
        run_broker()
    elif args.service == "ebest":
        asyncio.run(run_ebest())
    else:
        raise ValueError(f"Unknown service: {args.service}")


if __name__ == "__main__":
    main()

import asyncio
from datetime import datetime

from aiohttp import ClientSession
from httpx import Client

from delta.adapter.ebest.auth import get_access_token
from delta.adapter.ebest.websocket import create_topics, start_client
from delta.config import EBEST_REST_URL, EBEST_APP_KEY, EBEST_APP_SECRET, EBEST_WS_URL


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

from httpx import AsyncClient
from urllib.parse import urljoin

from delta.config import EBEST_APP_KEY, EBEST_APP_SECRET, EBEST_BASE_URL


async def get_access_token():
    headers = {"content-type": "application/x-www-form-urlencoded"}
    params = {
        "grant_type": "client_credentials",
        "appkey": EBEST_APP_KEY,
        "appsecretkey": EBEST_APP_SECRET,
        "scope": "oob",
    }
    path = "oauth2/token"
    url = urljoin(EBEST_BASE_URL, path)

    async with AsyncClient(verify=False) as client:
        response = await client.post(url, headers=headers, params=params)
        data = response.json()
        return data["access_token"]


async def post_t1764(shcode, gubun):
    pass

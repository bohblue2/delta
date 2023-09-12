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

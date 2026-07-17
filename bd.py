import requests
from datetime import datetime
from urllib.parse import urlencode


HOME_API = "https://www.btvlive.gov.bd/api/home"
TOKEN_API = "https://www.btvlive.gov.bd/api/cfToken"

OUTPUT = "bdt.m3u8"


HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.btvlive.gov.bd/"
}


def get_token():

    print("Getting CloudFront token...")

    r = requests.get(
        TOKEN_API,
        headers=HEADERS,
        timeout=30
    )

    r.raise_for_status()

    data = r.json()

    if data.get("status") != "success":
        raise Exception("Token failed")

    return data["output"]



def get_channels():

    r = requests.get(
        HOME_API,
        headers=HEADERS,
        timeout=30
    )

    r.raise_for_status()

    data = r.json()

    return data.get(
        "channel_list",
        []
    )



def add_token(url, token):

    return url + "?" + token



def create_m3u():

    token = get_token()

    channels = get_channels()

    print(
        "Channels:",
        len(channels)
    )


    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:


        f.write("#EXTM3U\n")

        f.write(
            "# Updated: "
            + str(datetime.now())
            + "\n\n"
        )


        for ch in channels:


            if ch.get("status") != "online":
                continue


            cid = ch.get(
                "channel_id"
            )

            name = ch.get(
                "channel_name"
            )

            logo = ch.get(
                "poster"
            )


            stream = (
                ch["base_url"]
                + ch["identifier"]
                + "/index.m3u8"
            )


            # Add CloudFront token
            stream = add_token(
                stream,
                token
            )


            f.write(
                f'#EXTINF:-1 '
                f'tvg-id="{cid}" '
                f'tvg-name="{name}" '
                f'group-title="Bangladesh TV" '
                f'tvg-logo="{logo}",'
                f'{name}\n'
            )


            f.write(
                "#EXTVLCOPT:http-referrer=https://www.btvlive.gov.bd/\n"
            )


            f.write(
                "#EXTVLCOPT:http-user-agent=Mozilla/5.0\n"
            )


            f.write(
                stream
                + "\n\n"
            )


            print(
                "Added:",
                name
            )


    print(
        "Created:",
        OUTPUT
    )



if __name__ == "__main__":
    create_m3u()

import requests
from datetime import datetime

API = "https://www.btvlive.gov.bd/api/home"
OUTPUT = "bdt.m3u8"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.btvlive.gov.bd/"
}


def create_playlist():

    session = requests.Session()

    response = session.get(
        API,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    # API cookie
    cookies = session.cookies.get_dict()

    cookie_string = "; ".join(
        [f"{k}={v}" for k, v in cookies.items()]
    )


    channels = data.get(
        "channel_list",
        []
    )


    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("#EXTM3U\n")


        for ch in channels:

            name = ch.get(
                "channel_name",
                "BTV"
            )

            logo = ch.get(
                "poster",
                ""
            )

            stream = ch.get(
                "count_url",
                ""
            )


            if ".m3u8" in stream:


                f.write(
                    '#EXTINF:-1 '
                    f'tvg-logo="{logo}" '
                    f'tvg-name="{name}",'
                    f'{name}\n'
                )


                # Cookie + Referer
                if cookie_string:

                    f.write(
                        f'#EXTVLCOPT:http-referrer={HEADERS["Referer"]}\n'
                    )

                    f.write(
                        f'#EXTVLCOPT:http-cookie={cookie_string}\n'
                    )


                f.write(
                    stream + "\n\n"
                )


    print(
        "Created:",
        OUTPUT,
        datetime.now()
    )


if __name__ == "__main__":
    create_playlist()

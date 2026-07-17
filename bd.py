import requests
from datetime import datetime

API = "https://www.btvlive.gov.bd/api/home"
OUTPUT = "bdt.m3u8"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def create_playlist():

    response = requests.get(
        API,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    channels = data.get("channel_list", [])

    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:

        file.write("#EXTM3U\n")

        for channel in channels:

            name = channel.get(
                "channel_name",
                "BTV"
            )

            stream = channel.get(
                "count_url",
                ""
            )

            if ".m3u8" in stream:

                file.write(
                    f'#EXTINF:-1,{name}\n'
                )

                file.write(
                    stream + "\n"
                )


    print(
        "Created:",
        OUTPUT,
        datetime.now()
    )


if __name__ == "__main__":
    create_playlist()

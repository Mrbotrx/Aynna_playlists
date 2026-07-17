import requests
from datetime import datetime

API = "https://www.btvlive.gov.bd/api/home"
OUTPUT = "bdt.m3u8"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.btvlive.gov.bd/"
}


def create_playlist():

    r = requests.get(
        API,
        headers=HEADERS,
        timeout=30
    )

    r.raise_for_status()

    data = r.json()

    channels = data.get("channel_list", [])

    if not channels:
        raise Exception("Channel list not found")


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

            name = ch.get(
                "channel_name",
                "BTV"
            )

            logo = ch.get(
                "poster",
                ""
            )

            base_url = ch.get(
                "base_url",
                ""
            )

            identifier = ch.get(
                "identifier",
                ""
            )


            if base_url and identifier:

                stream = (
                    base_url
                    + identifier
                    + "/playlist.m3u8"
                )


                f.write(
                    '#EXTINF:-1 '
                    f'tvg-id="{identifier}" '
                    f'tvg-logo="{logo}",'
                    f'{name}\n'
                )


                f.write(
                    '#EXTVLCOPT:http-referrer=https://www.btvlive.gov.bd/\n'
                )


                f.write(
                    stream
                    + "\n\n"
                )


    print("Created:", OUTPUT)
    print("Channels:", len(channels))


if __name__ == "__main__":
    create_playlist()

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

    channels = data.get("channel_list", [])

    if not channels:
        raise Exception("No channel found")


    with open(OUTPUT, "w", encoding="utf-8") as f:

        f.write("#EXTM3U\n")

        for ch in channels:

            name = ch.get("channel_name", "BTV")
            logo = ch.get("poster", "")

            base_url = ch.get("base_url", "")
            identifier = ch.get("identifier", "")

            if base_url and identifier:

                stream = (
                    base_url
                    + identifier
                    + "/playlist.m3u8"
                )

                f.write(
                    f'#EXTINF:-1 tvg-id="{identifier}" '
                    f'tvg-logo="{logo}",{name}\n'
                )

                f.write(
                    f'#EXTVLCOPT:http-referrer={HEADERS["Referer"]}\n'
                )

                f.write(
                    stream + "\n\n"
                )


    print("Updated:", OUTPUT)
    print("Channels:", len(channels))
    print(datetime.now())


if __name__ == "__main__":
    create_playlist()

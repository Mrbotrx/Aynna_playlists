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

    r = session.get(
        API,
        headers=HEADERS,
        timeout=30
    )

    r.raise_for_status()

    data = r.json()

    channels = data.get("channel_list", [])

    with open(OUTPUT, "w", encoding="utf-8") as f:

        f.write("#EXTM3U\n\n")

        for ch in channels:

            name = ch.get("channel_name", "BTV")
            logo = ch.get("poster", "")

            base = ch.get("base_url", "")
            identifier = ch.get("identifier", "")

            if base and identifier:

                stream = (
                    base
                    + identifier
                    + "/playlist.m3u8"
                )

                f.write(
                    f'#EXTINF:-1 tvg-logo="{logo}" tvg-name="{name}",{name}\n'
                )

                f.write(
                    f'#EXTVLCOPT:http-referrer={HEADERS["Referer"]}\n'
                )

                f.write(
                    stream + "\n\n"
                )


    print("Created", OUTPUT, datetime.now())


if __name__ == "__main__":
    create_playlist()

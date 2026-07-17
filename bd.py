import requests
from datetime import datetime, timezone

API = "https://www.btvlive.gov.bd/api/home"
OUTPUT = "bdt.m3u8"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.btvlive.gov.bd/"
}


def generate_playlist():

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
        raise Exception("Channel list empty")


    now = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )


    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("#EXTM3U\n")
        f.write(f"# Updated: {now}\n\n")


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
                    f'#EXTINF:-1 '
                    f'tvg-id="{identifier}" '
                    f'tvg-logo="{logo}",'
                    f'{name}\n'
                )

                f.write(
                    f'#EXTVLCOPT:http-referrer=https://www.btvlive.gov.bd/\n'
                )

                f.write(
                    stream + "\n\n"
                )


    print("Created:", OUTPUT)
    print("Channel:", len(channels))
    print("Updated:", now)



if __name__ == "__main__":
    generate_playlist()

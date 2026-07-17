import requests
from datetime import datetime

API = "https://www.btvlive.gov.bd/api/home"
OUTPUT = "bdt.m3u8"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.btvlive.gov.bd/"
}


def main():

    r = requests.get(
        API,
        headers=HEADERS,
        timeout=30
    )

    r.raise_for_status()

    data = r.json()

    channels = data.get("channel_list", [])

    if not channels:
        raise Exception("No channels found")


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

            name = ch.get("channel_name", "BTV")
            logo = ch.get("poster", "")

            base = ch.get("base_url", "")
            identifier = ch.get("identifier", "")

            if base and identifier:

                url = (
                    base
                    + identifier
                    + "/playlist.m3u8"
                )

                f.write(
                    f'#EXTINF:-1 tvg-logo="{logo}",{name}\n'
                )

                f.write(url + "\n\n")


    print("Created bdt.m3u8")
    print("Channels:", len(channels))


if __name__ == "__main__":
    main()

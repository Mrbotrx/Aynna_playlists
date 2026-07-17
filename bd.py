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

    print("Total channel:", len(channels))


    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("#EXTM3U\n")
        f.write("# Generated: " + str(datetime.now()) + "\n\n")


        for ch in channels:

            channel_id = ch.get("channel_id")
            identifier = ch.get("identifier")
            name = ch.get("channel_name")
            logo = ch.get("poster")
            base = ch.get("base_url")


            # stream url
            stream = (
                base
                + identifier
                + "/index.m3u8"
            )


            print(
                channel_id,
                identifier,
                stream
            )


            f.write(
                f'#EXTINF:-1 '
                f'tvg-id="{channel_id}" '
                f'tvg-logo="{logo}",'
                f'{name}\n'
            )

            f.write(
                stream
                + "\n\n"
            )


    print("Created:", OUTPUT)



if __name__ == "__main__":
    main()

import requests
from datetime import datetime


API_URL = "https://www.btvlive.gov.bd/api/home"

OUTPUT = "bdt.m3u8"


HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.btvlive.gov.bd/"
}


def main():

    print("Fetching BTV API...")

    r = requests.get(
        API_URL,
        headers=HEADERS,
        timeout=30
    )

    r.raise_for_status()

    data = r.json()

    channels = data.get(
        "channel_list",
        []
    )


    print(
        "Channels:",
        len(channels)
    )


    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:


        f.write(
            "#EXTM3U\n"
        )

        f.write(
            "# Updated: "
            + str(datetime.now())
            + "\n\n"
        )


        for ch in channels:


            if ch.get("status") != "online":
                continue


            cid = ch.get("channel_id")
            name = ch.get("channel_name")
            logo = ch.get("poster")


            stream = (
                ch.get("base_url")
                + ch.get("identifier")
                + "/index.m3u8"
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
                "#EXTVLCOPT:http-origin=https://www.btvlive.gov.bd\n"
            )

            f.write(
                "#EXTVLCOPT:http-user-agent=Mozilla/5.0\n"
            )


            f.write(
                stream
                + "\n\n"
            )


    print(
        "Updated:",
        OUTPUT
    )


if __name__ == "__main__":
    main()

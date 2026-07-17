import requests
from datetime import datetime


API_URL = "https://www.btvlive.gov.bd/api/home"

OUTPUT = "bdt.m3u8"


HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.btvlive.gov.bd/"
}


def update_playlist():

    response = requests.get(
        API_URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    channels = data.get("channel_list", [])

    print("Total channels:", len(channels))


    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:

        file.write("#EXTM3U\n")
        file.write(
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


            file.write(
                f'#EXTINF:-1 '
                f'tvg-id="{cid}" '
                f'tvg-name="{name}" '
                f'group-title="Bangladesh TV" '
                f'tvg-logo="{logo}",'
                f'{name}\n'
            )


            file.write(
                "#EXTVLCOPT:http-referrer=https://www.btvlive.gov.bd/\n"
            )

            file.write(
                "#EXTVLCOPT:http-origin=https://www.btvlive.gov.bd\n"
            )

            file.write(
                "#EXTVLCOPT:http-user-agent=Mozilla/5.0\n"
            )


            file.write(
                stream + "\n\n"
            )


    print("Updated:", OUTPUT)



if __name__ == "__main__":
    update_playlist()

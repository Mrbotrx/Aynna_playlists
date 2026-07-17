import requests
from datetime import datetime

API = "https://www.btvlive.gov.bd/api/home"
OUTPUT = "bdt.m3u8"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.btvlive.gov.bd/"
}


def get_channels():

    try:
        response = requests.get(
            API,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        return data.get("channel_list", [])

    except Exception as e:
        print("API Error:", e)
        return []


def create_m3u(channels):

    streams = set()

    with open(
        OUTPUT,
        "w",
        encoding="utf-8-sig"
    ) as file:

        file.write("#EXTM3U\n")
        file.write(
            "# Generated: "
            + str(datetime.now())
            + "\n\n"
        )


        total = 0

        for ch in channels:

            channel_id = ch.get("channel_id", "")
            name = ch.get("channel_name", "Unknown")
            logo = ch.get("poster", "")
            identifier = ch.get("identifier", "")
            base_url = ch.get("base_url", "")


            if not identifier or not base_url:
                continue


            stream_url = (
                base_url
                + identifier
                + "/index.m3u8"
            )


            if stream_url in streams:
                continue

            streams.add(stream_url)


            print(
                f"{channel_id} | {name}"
            )


            file.write(
                f'#EXTINF:-1 '
                f'group-title="Bangladesh TV" '
                f'tvg-id="{channel_id}" '
                f'tvg-logo="{logo}",'
                f'{name}\n'
            )


            file.write(
                stream_url
                + "\n\n"
            )


            total += 1


    print("-------------------------")
    print("Total channels:", total)
    print("Created:", OUTPUT)



def main():

    print("Fetching channels...")

    channels = get_channels()

    if not channels:
        print("No channel found")
        return


    create_m3u(channels)



if __name__ == "__main__":
    main()

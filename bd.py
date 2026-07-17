import requests
import json

API = "https://www.btvlive.gov.bd/api/home"
OUTPUT = "bdt.m3u8"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.btvlive.gov.bd/"
}


def main():

    r = requests.get(API, headers=headers, timeout=30)
    print("Status:", r.status_code)

    data = r.json()

    print("Keys:", data.keys())

    channels = data.get("channel_list", [])

    print("Channels:", len(channels))


    with open(OUTPUT, "w", encoding="utf-8") as f:

        f.write("#EXTM3U\n\n")

        for ch in channels:

            name = ch.get("channel_name")
            logo = ch.get("poster")
            url = ch.get("count_url")

            print(name, url)

            if url:

                f.write(
                    f'#EXTINF:-1 tvg-logo="{logo}",{name}\n'
                )

                f.write(
                    url + "\n\n"
                )


    print("DONE:", OUTPUT)


if __name__ == "__main__":
    main()

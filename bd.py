# bd.py

import requests

API = "https://www.btvlive.gov.bd/api/home"
OUTPUT = "bdtv.m3u8"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def find_streams(obj, output):
    if isinstance(obj, dict):
        name = (
            obj.get("name")
            or obj.get("title")
            or obj.get("channel_name")
            or obj.get("channel")
        )

        url = (
            obj.get("m3u8")
            or obj.get("stream_url")
            or obj.get("play_url")
            or obj.get("url")
        )

        if name and url and ".m3u8" in url:
            output.write(f"#EXTINF:-1,{name}\n")
            output.write(url + "\n")

        for value in obj.values():
            find_streams(value, output)

    elif isinstance(obj, list):
        for item in obj:
            find_streams(item, output)


def main():
    r = requests.get(API, headers=HEADERS, timeout=30)
    r.raise_for_status()

    data = r.json()

    with open(OUTPUT, "w", encoding="utf-8") as output:
        output.write("#EXTM3U\n")
        find_streams(data, output)

    print(f"Done! Created {OUTPUT}")


if __name__ == "__main__":
    main()

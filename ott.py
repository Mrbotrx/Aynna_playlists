import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


API_URL = os.getenv("API_URL_ottplus")
API_KEY = os.getenv("API_KEY")

OUTPUT_FILE = "OTTPLUS.m3u8"


HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

if API_KEY:
    HEADERS["Authorization"] = f"Bearer {API_KEY}"


def fetch_api():

    if not API_URL:
        raise Exception("API_URL_ottplus missing")

    print("Downloading API data...")

    r = requests.get(
        API_URL,
        headers=HEADERS,
        timeout=30
    )

    print("API Status:", r.status_code)

    r.raise_for_status()

    data = r.json()

    if isinstance(data, dict):
        for key in ["data", "channels", "results", "live"]:
            if key in data:
                data = data[key]
                break

    return data



def check_stream(url):

    if not url:
        return False

    try:
        r = requests.get(
            url,
            timeout=10,
            stream=True,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        return r.status_code == 200

    except:
        return False



def get_stream(ch):

    return (
        ch.get("url")
        or ch.get("stream")
        or ch.get("stream_url")
        or ch.get("m3u8")
        or ""
    )



def validate(ch):

    stream = get_stream(ch)

    if not check_stream(stream):
        return None

    return {
        "name": ch.get("name", "Unknown"),
        "logo": ch.get("logo", ""),
        "group": ch.get("group", "OTTPLUS"),
        "stream": stream
    }



def create_playlist(channels):

    print("Checking channels...")

    working = []

    with ThreadPoolExecutor(max_workers=20) as exe:

        tasks = [
            exe.submit(validate, ch)
            for ch in channels
        ]

        for t in as_completed(tasks):

            result = t.result()

            if result:
                working.append(result)


    # duplicate remove

    unique = {}

    for ch in working:
        unique[ch["stream"]] = ch


    working = list(unique.values())


    working.sort(
        key=lambda x:x["name"].lower()
    )


    print(
        "Working channels:",
        len(working)
    )


    # Always create file

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("#EXTM3U\n")

        for ch in working:

            f.write(
                f'#EXTINF:-1 '
                f'tvg-name="{ch["name"]}" '
                f'tvg-logo="{ch["logo"]}" '
                f'group-title="{ch["group"]}",'
                f'{ch["name"]}\n'
            )

            f.write(
                ch["stream"] + "\n"
            )


    print(
        "Saved:",
        OUTPUT_FILE
    )



def main():

    channels = fetch_api()

    create_playlist(
        channels
    )


if __name__ == "__main__":
    main()

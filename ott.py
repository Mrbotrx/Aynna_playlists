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



def fetch_json():

    if not API_URL:
        raise Exception(
            "API_URL_ottplus missing"
        )

    print("Downloading JSON API...")

    r = requests.get(
        API_URL,
        headers=HEADERS,
        timeout=30
    )

    print(
        "API Status:",
        r.status_code
    )

    print(
        "Content-Type:",
        r.headers.get("content-type")
    )


    r.raise_for_status()


    data = r.json()


    # Support common JSON formats

    if isinstance(data, dict):

        for key in [
            "data",
            "channels",
            "results",
            "live",
            "items"
        ]:

            if key in data:
                data = data[key]
                break


    if not isinstance(data, list):

        raise Exception(
            "JSON channel list not found"
        )


    print(
        "Channels found:",
        len(data)
    )


    return data



def get_stream(ch):

    return (
        ch.get("url")
        or ch.get("stream")
        or ch.get("stream_url")
        or ch.get("m3u8")
        or ch.get("play_url")
        or ""
    )



def check_url(url):

    if not url:
        return False

    try:

        r = requests.get(
            url,
            timeout=10,
            stream=True,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )

        return r.status_code == 200


    except:

        return False



def check_channel(ch):

    stream = get_stream(ch)

    if not check_url(stream):
        return None


    return {

        "name":
            ch.get(
                "name",
                "Unknown"
            ),

        "logo":
            ch.get(
                "logo",
                ""
            ),

        "group":
            ch.get(
                "group",
                "OTTPLUS"
            ),

        "stream":
            stream
    }



def create_m3u(channels):

    print(
        "Checking streams..."
    )

    valid = []


    with ThreadPoolExecutor(
        max_workers=20
    ) as executor:


        jobs = [
            executor.submit(
                check_channel,
                ch
            )
            for ch in channels
        ]


        for job in as_completed(jobs):

            result = job.result()

            if result:
                valid.append(result)



    # remove duplicates

    unique = {}

    for ch in valid:
        unique[ch["stream"]] = ch


    valid = list(
        unique.values()
    )


    valid.sort(
        key=lambda x:
        x["name"].lower()
    )


    print(
        "Working channels:",
        len(valid)
    )


    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:


        f.write(
            "#EXTM3U\n"
        )


        for ch in valid:

            f.write(
                f'#EXTINF:-1 '
                f'tvg-name="{ch["name"]}" '
                f'tvg-logo="{ch["logo"]}" '
                f'group-title="{ch["group"]}",'
                f'{ch["name"]}\n'
            )

            f.write(
                ch["stream"]
                + "\n"
            )


    print(
        "Saved:",
        OUTPUT_FILE
    )



def main():

    channels = fetch_json()

    create_m3u(
        channels
    )


if __name__ == "__main__":

    main()

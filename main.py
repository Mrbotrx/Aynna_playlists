import os
import json
import re
import requests


API_URL = os.environ.get("AYNAOTT_API_URL")

OUTPUT_DIR = "output"

API_JSON = os.path.join(
    OUTPUT_DIR,
    "aynaott_api.json"
)

M3U8_FILE = os.path.join(
    OUTPUT_DIR,
    "aynnaott.m3u8"
)

DEBUG_FILE = os.path.join(
    OUTPUT_DIR,
    "debug_urls.txt"
)


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


def fetch_api():

    if not API_URL:
        raise Exception(
            "AYNAOTT_API_URL secret missing"
        )

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    response = requests.get(
        API_URL,
        headers=headers,
        timeout=30
    )

    print(
        "API Status:",
        response.status_code
    )

    response.raise_for_status()

    return response.json()



def save_json(data):

    with open(
        API_JSON,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(
        "Saved:",
        API_JSON
    )



def scan_m3u8(
        data,
        channels=None,
        urls=None,
        channel_name="Unknown"
):

    if channels is None:
        channels = []

    if urls is None:
        urls = []


    if isinstance(data, dict):

        name = (
            data.get("name")
            or data.get("title")
            or data.get("channelName")
            or data.get("channel")
            or channel_name
        )


        for key, value in data.items():

            if isinstance(value, str):

                if value.startswith("http"):

                    urls.append(value)


                if re.search(
                    r"\.m3u8",
                    value,
                    re.IGNORECASE
                ):

                    channels.append(
                        {
                            "name": name,
                            "url": value
                        }
                    )


            elif isinstance(
                value,
                (dict, list)
            ):

                scan_m3u8(
                    value,
                    channels,
                    urls,
                    name
                )


    elif isinstance(data, list):

        for item in data:

            scan_m3u8(
                item,
                channels,
                urls,
                channel_name
            )


    return channels, urls



def remove_duplicate(channels):

    result = []
    seen = set()


    for ch in channels:

        url = ch["url"]

        if url not in seen:

            seen.add(url)

            result.append(ch)


    return result



def save_debug_urls(urls):

    with open(
        DEBUG_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        for url in urls:

            f.write(
                url + "\n"
            )



def create_m3u8(channels):

    with open(
        M3U8_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        # Always create playlist
        f.write(
            "#EXTM3U\n\n"
        )


        if channels:

            for ch in channels:

                f.write(
                    f'#EXTINF:-1,{ch["name"]}\n'
                )

                f.write(
                    f'{ch["url"]}\n'
                )

        else:

            f.write(
                "# No m3u8 stream found\n"
            )


    print(
        "Created:",
        M3U8_FILE
    )



def main():

    print(
        "Starting..."
    )


    data = fetch_api()


    save_json(
        data
    )


    channels, urls = scan_m3u8(
        data
    )


    save_debug_urls(
        urls
    )


    channels = remove_duplicate(
        channels
    )


    print(
        "Total URL:",
        len(urls)
    )

    print(
        "m3u8 Found:",
        len(channels)
    )


    # Always create file
    create_m3u8(
        channels
    )


    print(
        "Finished"
    )



if __name__ == "__main__":
    main()

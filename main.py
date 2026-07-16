import os
import json
import re
import requests


API_URL = os.environ.get("AYNAOTT_API_URL")

OUTPUT_DIR = "output"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

API_FILE = "output/aynaott_api.json"
M3U8_FILE = "output/aynnaott.m3u8"



def fetch_api():

    if not API_URL:
        raise Exception("Missing AYNAOTT_API_URL")


    response = requests.get(
        API_URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()



def find_m3u8(data, result=None, name="Unknown"):

    if result is None:
        result = []


    if isinstance(data, dict):

        channel = (
            data.get("name")
            or data.get("title")
            or data.get("channelName")
            or name
        )


        for key, value in data.items():

            if isinstance(value, str):

                if ".m3u8" in value:

                    result.append({
                        "name": channel,
                        "url": value
                    })


            elif isinstance(value, (dict, list)):

                find_m3u8(
                    value,
                    result,
                    channel
                )


    elif isinstance(data, list):

        for item in data:

            find_m3u8(
                item,
                result,
                name
            )


    return result



def create_m3u8(channels):

    with open(
        M3U8_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("#EXTM3U\n")


        for ch in channels:

            f.write(
                f'#EXTINF:-1,{ch["name"]}\n'
            )

            f.write(
                ch["url"] + "\n"
            )


    print(
        "Created:",
        M3U8_FILE
    )



def main():

    try:

        data = fetch_api()


    except Exception as e:

        print(e)

        data = {}


    with open(
        API_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


    channels = find_m3u8(
        data
    )


    print(
        "Found:",
        len(channels)
    )


    # সবসময় m3u8 তৈরি হবে
    create_m3u8(
        channels
    )



if __name__ == "__main__":
    main()

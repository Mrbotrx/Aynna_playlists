import os
import json
import re
import requests


API_URL = os.environ.get("AYNAOTT_API_URL")

OUTPUT_DIR = "output"

API_FILE = os.path.join(
    OUTPUT_DIR,
    "aynaott_api.json"
)

M3U8_FILE = os.path.join(
    OUTPUT_DIR,
    "aynnaott.m3u8"
)


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


def get_api_data():

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

    response.raise_for_status()

    return response.json()



def save_api_json(data):

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



def find_m3u8(
    data,
    result=None,
    channel="Unknown"
):

    if result is None:
        result = []


    if isinstance(data, dict):

        name = (
            data.get("name")
            or data.get("title")
            or data.get("channelName")
            or data.get("channel")
            or channel
        )


        for key, value in data.items():

            if isinstance(value, str):

                if re.search(
                    r"https?://.*?\.m3u8",
                    value
                ):

                    result.append(
                        {
                            "name": name,
                            "url": value
                        }
                    )


            elif isinstance(
                value,
                (dict, list)
            ):

                find_m3u8(
                    value,
                    result,
                    name
                )


    elif isinstance(data, list):

        for item in data:

            find_m3u8(
                item,
                result,
                channel
            )


    return result



def remove_duplicate(items):

    seen = set()
    output = []

    for item in items:

        if item["url"] not in seen:

            seen.add(
                item["url"]
            )

            output.append(
                item
            )

    return output



def create_m3u8(channels):

    with open(
        M3U8_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "#EXTM3U\n"
        )


        for ch in channels:

            f.write(
                f'#EXTINF:-1,{ch["name"]}\n'
            )

            f.write(
                f'{ch["url"]}\n'
            )


    print(
        "Created:",
        M3U8_FILE
    )



def main():

    print(
        "Downloading API..."
    )

    data = get_api_data()


    save_api_json(
        data
    )


    channels = find_m3u8(
        data
    )


    channels = remove_duplicate(
        channels
    )


    print(
        "Found m3u8:",
        len(channels)
    )


    if channels:

        create_m3u8(
            channels
        )

    else:

        print(
            "No m3u8 URL found. Check aynaott_api.json"
        )



if __name__ == "__main__":
    main()

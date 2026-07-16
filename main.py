import os
import json
import requests


API_URL = os.environ.get("AYNAOTT_API_URL")

OUTPUT_DIR = "output"

API_JSON_FILE = os.path.join(
    OUTPUT_DIR,
    "aynaott_api.json"
)

M3U_FILE = os.path.join(
    OUTPUT_DIR,
    "aynaott_channels.m3u"
)


def fetch_api():
    print("[+] Fetching API...")

    if not API_URL:
        raise Exception(
            "AYNAOTT_API_URL secret missing"
        )

    response = requests.get(
        API_URL,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    return response.json()



def find_m3u8(
    data,
    results=None,
    channel_name="Unknown"
):

    if results is None:
        results = []


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

                if ".m3u8" in value:

                    results.append(
                        {
                            "channel": name,
                            "url": value
                        }
                    )


            elif isinstance(
                value,
                (dict, list)
            ):

                find_m3u8(
                    value,
                    results,
                    name
                )


    elif isinstance(data, list):

        for item in data:

            find_m3u8(
                item,
                results,
                channel_name
            )


    return results



def save_json(data):

    with open(
        API_JSON_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


    print(
        "[+] Saved:",
        API_JSON_FILE
    )



def remove_duplicate(channels):

    unique = []
    urls = set()

    for item in channels:

        if item["url"] not in urls:

            urls.add(
                item["url"]
            )

            unique.append(
                item
            )

    return unique



def create_m3u(channels):

    with open(
        M3U_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "#EXTM3U\n"
        )


        for ch in channels:

            file.write(
                f'#EXTINF:-1,{ch["channel"]}\n'
            )

            file.write(
                f'{ch["url"]}\n'
            )


    print(
        "[+] Created:",
        M3U_FILE
    )



def main():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )


    api_data = fetch_api()


    save_json(
        api_data
    )


    channels = find_m3u8(
        api_data
    )


    channels = remove_duplicate(
        channels
    )


    print(
        "[+] m3u8 Found:",
        len(channels)
    )


    create_m3u(
        channels
    )


    for ch in channels[:10]:

        print(
            ch["channel"],
            "=>",
            ch["url"]
        )



if __name__ == "__main__":
    main()

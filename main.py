import os
import re
import requests


API_URL = os.environ.get("AYNAOTT_API_URL")

OUTPUT_DIR = "output"

PLAYLIST_FILE = os.path.join(
    OUTPUT_DIR,
    "aynnaott.m3u8"
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


    response = requests.get(
        API_URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        },
        timeout=30
    )


    print(
        "API Status:",
        response.status_code
    )


    response.raise_for_status()

    return response.json()



def find_m3u8(
    data,
    result=None,
    channel_name="Unknown"
):

    if result is None:
        result = []


    if isinstance(data, dict):

        name = (
            data.get("name")
            or data.get("title")
            or data.get("channelName")
            or data.get("channel")
            or channel_name
        )


        for value in data.values():

            if isinstance(value, str):

                if re.search(
                    r"https?://.*?\.m3u8",
                    value,
                    re.IGNORECASE
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
                channel_name
            )


    return result



def remove_duplicate(channels):

    unique = []
    seen = set()


    for item in channels:

        url = item["url"]

        if url not in seen:

            seen.add(url)

            unique.append(item)


    return unique



def create_playlist(channels):

    with open(
        PLAYLIST_FILE,
        "w",
        encoding="utf-8"
    ) as file:


        file.write(
            "#EXTM3U\n"
        )


        for channel in channels:

            file.write(
                f'#EXTINF:-1,{channel["name"]}\n'
            )

            file.write(
                f'{channel["url"]}\n'
            )


        if not channels:

            file.write(
                "# No m3u8 stream found\n"
            )


    print(
        "Created:",
        PLAYLIST_FILE
    )



def main():

    try:

        data = fetch_api()


        channels = find_m3u8(
            data
        )


        channels = remove_duplicate(
            channels
        )


        print(
            "m3u8 Found:",
            len(channels)
        )


    except Exception as error:

        print(
            "Error:",
            error
        )

        channels = []


    # সবসময় playlist তৈরি হবে
    create_playlist(
        channels
    )



if __name__ == "__main__":
    main()

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
            "AYNAOTT_API_URL missing"
        )


    response = requests.get(
        API_URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()



def find_channels(
        data,
        channels=None,
        name="Unknown",
        logo=""
):

    if channels is None:
        channels = []


    if isinstance(data, dict):

        channel_name = (
            data.get("name")
            or data.get("title")
            or data.get("channelName")
            or data.get("channel")
            or name
        )


        channel_logo = (
            data.get("logo")
            or data.get("image")
            or data.get("icon")
            or data.get("thumbnail")
            or logo
        )


        for key, value in data.items():


            if isinstance(value, str):


                # Find m3u8
                if re.search(
                    r"https?://.*?\.m3u8",
                    value,
                    re.IGNORECASE
                ):

                    channels.append(
                        {
                            "name": channel_name,
                            "url": value,
                            "logo": channel_logo
                        }
                    )


            elif isinstance(
                value,
                (dict, list)
            ):

                find_channels(
                    value,
                    channels,
                    channel_name,
                    channel_logo
                )


    elif isinstance(data, list):

        for item in data:

            find_channels(
                item,
                channels,
                name,
                logo
            )


    return channels



def remove_duplicate(channels):

    result = []

    seen = set()


    for ch in channels:

        if ch["url"] not in seen:

            seen.add(
                ch["url"]
            )

            result.append(
                ch
            )


    return result



def create_playlist(channels):


    with open(
        PLAYLIST_FILE,
        "w",
        encoding="utf-8"
    ) as file:


        file.write(
            "#EXTM3U\n\n"
        )


        for ch in channels:


            name = ch["name"]

            url = ch["url"]

            logo = ch.get(
                "logo",
                ""
            )


            file.write(
                f'#EXTINF:-1 tvg-name="{name}" tvg-logo="{logo}" group-title="Live TV",{name}\n'
            )


            file.write(
                url + "\n\n"
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


        channels = find_channels(
            data
        )


        channels = remove_duplicate(
            channels
        )


        print(
            "Channels:",
            len(channels)
        )


    except Exception as e:

        print(
            "Error:",
            e
        )

        channels = []


    # Always create playlist
    create_playlist(
        channels
    )



if __name__ == "__main__":

    main()

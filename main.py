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


    r = requests.get(
        API_URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        },
        timeout=30
    )


    print(
        "API Status:",
        r.status_code
    )


    r.raise_for_status()

    return r.json()



def find_channels(
        data,
        channels=None,
        name="Unknown",
        logo="",
        group="Live TV"
):

    if channels is None:
        channels = []


    if isinstance(data, dict):


        channel_name = (
            data.get("name")
            or data.get("title")
            or data.get("channelName")
            or data.get("channel_name")
            or name
        )


        channel_logo = (
            data.get("logo")
            or data.get("logoUrl")
            or data.get("logo_url")
            or data.get("image")
            or data.get("imageUrl")
            or data.get("thumbnail")
            or data.get("icon")
            or data.get("poster")
            or logo
        )


        channel_group = (
            data.get("group")
            or data.get("groupName")
            or data.get("category")
            or data.get("genre")
            or data.get("type")
            or data.get("section")
            or group
        )


        for key, value in data.items():


            if isinstance(value, str):


                if re.search(
                    r"https?://.*?\.m3u8",
                    value,
                    re.IGNORECASE
                ):


                    channels.append(
                        {
                            "name": channel_name,
                            "url": value,
                            "logo": channel_logo,
                            "group": channel_group
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
                    channel_logo,
                    channel_group
                )



    elif isinstance(data, list):


        for item in data:


            find_channels(
                item,
                channels,
                name,
                logo,
                group
            )


    return channels



def remove_duplicate(channels):

    result = []

    seen = set()


    for ch in channels:


        url = ch["url"]


        if url not in seen:


            seen.add(url)

            result.append(ch)


    return result



def create_playlist(channels):


    with open(
        PLAYLIST_FILE,
        "w",
        encoding="utf-8"
    ) as f:


        f.write(
            "#EXTM3U\n\n"
        )


        for ch in channels:


            name = ch.get(
                "name",
                "Unknown"
            )


            url = ch.get(
                "url",
                ""
            )


            logo = ch.get(
                "logo",
                ""
            )


            group = ch.get(
                "group",
                "Live TV"
            )


            f.write(
                f'#EXTINF:-1 tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}\n'
            )


            f.write(
                url + "\n\n"
            )


        if not channels:


            f.write(
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
            "Found channels:",
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

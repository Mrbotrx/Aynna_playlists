import os
import json
import requests
import re


API_URL = os.environ.get("AYNAOTT_API_URL")


os.makedirs(
    "output",
    exist_ok=True
)


API_FILE = "output/aynaott_api.json"

PLAYLIST_FILE = "output/aynnaott.m3u8"



def fetch_api():

    if not API_URL:
        raise Exception(
            "API URL missing"
        )


    r = requests.get(
        API_URL,
        headers={
            "User-Agent":"Mozilla/5.0"
        },
        timeout=30
    )

    r.raise_for_status()

    return r.json()



def find_m3u8(
    data,
    result=None,
    name="Unknown"
):

    if result is None:
        result=[]


    if isinstance(data,dict):

        channel = (
            data.get("name")
            or data.get("title")
            or data.get("channelName")
            or name
        )


        for value in data.values():

            if isinstance(value,str):

                if ".m3u8" in value:

                    result.append(
                        {
                            "name":channel,
                            "url":value
                        }
                    )


            elif isinstance(value,(dict,list)):

                find_m3u8(
                    value,
                    result,
                    channel
                )


    elif isinstance(data,list):

        for item in data:

            find_m3u8(
                item,
                result,
                name
            )


    return result



def create_playlist(channels):

    with open(
        PLAYLIST_FILE,
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
                ch["url"]+"\n"
            )


        if not channels:

            f.write(
                "# No stream found\n"
            )


    print(
        "Created:",
        PLAYLIST_FILE
    )



def main():

    try:

        data = fetch_api()

    except Exception as e:

        print(e)

        data={}


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


    channels=find_m3u8(
        data
    )


    print(
        "Found:",
        len(channels)
    )


    create_playlist(
        channels
    )



if __name__=="__main__":
    main()

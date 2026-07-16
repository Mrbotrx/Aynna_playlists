import os
import json
import requests


API_URL = os.environ.get("AYNAOTT_API_URL")


def get_api():

    if not API_URL:
        raise Exception("API URL missing")

    response = requests.get(
        API_URL,
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


        for key,value in data.items():

            if isinstance(value,str):

                if ".m3u8" in value:

                    result.append({
                        "channel": channel,
                        "url": value
                    })


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



api = get_api()


with open(
    "aynaott_api.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        api,
        f,
        indent=4,
        ensure_ascii=False
    )


channels = find_m3u8(api)


with open(
    "aynaott_channels.m3u",
    "w",
    encoding="utf-8"
) as f:

    f.write("#EXTM3U\n")

    for c in channels:

        f.write(
            f'#EXTINF:-1,{c["channel"]}\n'
        )

        f.write(
            c["url"]+"\n"
        )


print(
    "Found channels:",
    len(channels)
)

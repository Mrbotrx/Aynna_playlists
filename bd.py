import requests
from datetime import datetime


HOME_API = "https://www.btvlive.gov.bd/api/home"
TOKEN_API = "https://www.btvlive.gov.bd/api/cfToken"

OUTPUT = "bdt.m3u8"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "Chrome/128.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://www.btvlive.gov.bd/"
}



def get_cf_token():

    print("Getting CloudFront token...")

    r = requests.get(
        TOKEN_API,
        headers=HEADERS,
        timeout=30
    )

    r.raise_for_status()

    data = r.json()


    if data.get("status") != "success":

        raise Exception(
            "Token API failed"
        )


    token = data.get(
        "output"
    )


    if not token:

        raise Exception(
            "Token not found"
        )


    print("Token OK")

    return token




def get_channels():

    print("Getting channels...")

    r = requests.get(
        HOME_API,
        headers=HEADERS,
        timeout=30
    )


    r.raise_for_status()


    data = r.json()


    return data.get(
        "channel_list",
        []
    )




def create_playlist():


    token = get_cf_token()


    channels = get_channels()


    print(
        "Total channels:",
        len(channels)
    )



    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:


        f.write(
            "#EXTM3U\n"
        )


        f.write(
            "# Updated: "
            + str(datetime.now())
            + "\n\n"
        )



        for ch in channels:


            if ch.get("status") != "online":

                continue



            channel_id = ch.get(
                "channel_id"
            )


            name = ch.get(
                "channel_name",
                "Unknown"
            )


            logo = ch.get(
                "poster",
                ""
            )



            stream = (
                ch.get("base_url")
                + ch.get("identifier")
                + "/index.m3u8"
            )



            # CloudFront signed token add

            stream = (
                stream
                + "?"
                + token
            )



            print(
                "Added:",
                name
            )



            f.write(
                f'#EXTINF:-1 '
                f'tvg-id="{channel_id}" '
                f'tvg-name="{name}" '
                f'group-title="Bangladesh TV" '
                f'tvg-logo="{logo}",'
                f'{name}\n'
            )



            # Player headers

            f.write(
                "#EXTVLCOPT:http-referrer=https://www.btvlive.gov.bd/\n"
            )


            f.write(
                "#EXTVLCOPT:http-origin=https://www.btvlive.gov.bd\n"
            )


            f.write(
                "#EXTVLCOPT:http-user-agent="
                "Mozilla/5.0\n"
            )



            f.write(
                stream
                + "\n\n"
            )



    print("----------------------")

    print(
        "Playlist Updated:",
        OUTPUT
    )





if __name__ == "__main__":

    create_playlist()

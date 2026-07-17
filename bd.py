import requests
from datetime import datetime
from urllib.parse import urlencode


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

    print("Token API response:")
    print(data)


    if data.get("status") != "success":
        raise Exception("Token API failed")


    output = data.get("output")


    if not output:
        raise Exception("Token output missing")


    # Already formatted token string
    if isinstance(output, str):

        token = output.strip()

        # remove starting ?
        token = token.lstrip("?")

        if "Key-Pair-Id" not in token:
            raise Exception(
                "CloudFront token missing Key-Pair-Id"
            )

        print("Token OK")

        return token


    # JSON token object
    if isinstance(output, dict):

        required = [
            "Expires",
            "Signature",
            "Key-Pair-Id"
        ]

        for key in required:
            if key not in output:
                raise Exception(
                    f"Missing CloudFront field: {key}"
                )


        token = urlencode({
            "Expires": output["Expires"],
            "Signature": output["Signature"],
            "Key-Pair-Id": output["Key-Pair-Id"]
        })


        print("Token OK")

        return token



    raise Exception(
        "Unknown token format"
    )



def get_channels():

    print("Getting channels...")


    r = requests.get(
        HOME_API,
        headers=HEADERS,
        timeout=30
    )


    r.raise_for_status()


    data = r.json()


    channels = data.get(
        "channel_list",
        []
    )


    if not channels:
        raise Exception(
            "No channels found"
        )


    return channels




def add_token(url, token):

    if "?" in url:
        return url + "&" + token

    return url + "?" + token




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


        f.write("#EXTM3U\n")

        f.write(
            "# Updated: "
            + str(datetime.now())
            + "\n\n"
        )


        count = 0


        for ch in channels:


            if ch.get("status") != "online":
                continue


            channel_id = ch.get(
                "channel_id",
                ""
            )


            name = ch.get(
                "channel_name",
                "Unknown"
            )


            logo = ch.get(
                "poster",
                ""
            )


            base = ch.get(
                "base_url"
            )


            identifier = ch.get(
                "identifier"
            )


            if not base or not identifier:
                continue


            stream = (
                base
                + identifier
                + "/index.m3u8"
            )


            stream = add_token(
                stream,
                token
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


            count += 1



    print("----------------------")
    print(
        "Playlist Updated:",
        OUTPUT
    )

    print(
        "Working streams:",
        count
    )



if __name__ == "__main__":

    create_playlist()

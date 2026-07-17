import requests
import os
from datetime import datetime


# ================= CONFIG =================

API_URL = "https://www.btvlive.gov.bd/api/home"

OUTPUT_FILE = "bdt.m3u8"

REFERRER = "https://www.btvlive.gov.bd/"
ORIGIN = "https://www.btvlive.gov.bd/"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/128.0 Safari/537.36"
)


# =========================================


def fetch_channels():

    try:

        print("Connecting API...")

        r = requests.get(
            API_URL,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
                "Referer": REFERRER
            },
            timeout=30
        )


        print(
            "API Status:",
            r.status_code
        )


        r.raise_for_status()


        data = r.json()


        return data.get(
            "channel_list",
            []
        )


    except Exception as e:

        print(
            "API Error:",
            e
        )

        return []




def create_playlist(channels):


    if not channels:

        print(
            "No channels found"
        )

        return



    temp_file = OUTPUT_FILE + ".tmp"


    used = set()

    count = 0



    with open(
        temp_file,
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



            cid = ch.get(
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


            base = ch.get(
                "base_url",
                ""
            )


            identifier = ch.get(
                "identifier",
                ""
            )


            if not base or not identifier:

                continue



            stream = (
                base
                + identifier
                + "/index.m3u8"
            )



            if stream in used:

                continue


            used.add(stream)



            # EXTINF

            f.write(
                '#EXTINF:-1 '
                f'tvg-id="{cid}" '
                f'tvg-name="{name}" '
                f'group-title="Bangladesh TV" '
                f'tvg-logo="{logo}",'
                f'{name}\n'
            )


            # VLC headers

            f.write(
                "#EXTVLCOPT:http-referrer="
                + REFERRER
                + "\n"
            )


            f.write(
                "#EXTVLCOPT:http-origin="
                + ORIGIN
                + "\n"
            )


            f.write(
                "#EXTVLCOPT:http-user-agent="
                + USER_AGENT
                + "\n"
            )


            # Stream URL

            f.write(
                stream
                + "\n\n"
            )


            count += 1


    # replace old file

    os.replace(
        temp_file,
        OUTPUT_FILE
    )


    print("----------------------")
    print(
        "Playlist Updated"
    )
    print(
        "Channels:",
        count
    )
    print(
        "File:",
        os.path.abspath(OUTPUT_FILE)
    )




def main():


    channels = fetch_channels()


    create_playlist(
        channels
    )



if __name__ == "__main__":

    main()

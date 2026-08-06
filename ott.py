import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


# GitHub Secrets থেকে নেওয়া হবে
API_URL = os.getenv("API_URL_ottplus")
API_KEY = os.getenv("API_KEY")

OUTPUT_FILE = "OTTPLUS.m3u8"


HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

if API_KEY:
    HEADERS["Authorization"] = f"Bearer {API_KEY}"


def check_url(url, timeout=10):
    if not url:
        return False

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=timeout,
            stream=True,
            allow_redirects=True
        )

        return response.status_code == 200

    except requests.RequestException:
        return False



def get_stream(channel):

    return (
        channel.get("url")
        or channel.get("stream_url")
        or channel.get("stream")
        or channel.get("m3u8")
        or ""
    )



def check_channel(channel):

    name = channel.get(
        "name",
        "Unknown"
    )

    logo = channel.get(
        "logo",
        ""
    )

    stream = get_stream(channel)


    if not stream:
        return None


    if not check_url(stream):
        return None


    # Logo check
    if logo and not check_url(logo):
        logo = ""


    return {
        "name": name,
        "logo": logo,
        "stream": stream,
        "group": channel.get(
            "group",
            "OTTPLUS"
        )
    }



def fetch_api():

    if not API_URL:
        raise Exception(
            "Missing API_URL_ottplus"
        )


    print("Downloading API data...")


    response = requests.get(
        API_URL,
        headers=HEADERS,
        timeout=30
    )


    response.raise_for_status()


    data = response.json()


    # যদি API response এ list এর ভিতরে data থাকে
    if isinstance(data, dict):

        for key in [
            "data",
            "channels",
            "results",
            "live"
        ]:
            if key in data:
                data = data[key]
                break


    return data



def create_m3u(channels):


    print(
        "Checking channels..."
    )


    working = []


    with ThreadPoolExecutor(
        max_workers=20
    ) as executor:


        jobs = [
            executor.submit(
                check_channel,
                ch
            )
            for ch in channels
        ]


        for job in as_completed(jobs):

            result = job.result()

            if result:
                working.append(result)



    # Duplicate remove

    unique = {}

    for channel in working:
        unique[
            channel["stream"]
        ] = channel


    working = list(
        unique.values()
    )


    # Alphabetical sorting

    working.sort(
        key=lambda x:
        x["name"].lower()
    )



    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:


        file.write(
            "#EXTM3U\n"
        )


        for ch in working:


            file.write(
                f'#EXTINF:-1 '
                f'tvg-name="{ch["name"]}" '
                f'tvg-logo="{ch["logo"]}" '
                f'group-title="{ch["group"]}",'
                f'{ch["name"]}\n'
            )


            file.write(
                ch["stream"] +
                "\n"
            )



    print(
        "Finished"
    )

    print(
        "Working channels:",
        len(working)
    )

    print(
        "Output:",
        OUTPUT_FILE
    )



def main():

    channels = fetch_api()

    create_m3u(
        channels
    )



if __name__ == "__main__":
    main()

import os
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


API_URL = os.getenv("API_URL_ottplus")
API_KEY = os.getenv("API_KEY")

OUTPUT_FILE = "OTTPLUS.m3u8"


HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Connection": "keep-alive"
}


if API_KEY:
    HEADERS["Authorization"] = f"Bearer {API_KEY}"



def request_api(url, retry=3):

    for attempt in range(retry):

        try:

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=30
            )


            print(
                "API Status:",
                response.status_code
            )


            if response.status_code == 403:

                print(
                    "403 Forbidden: API rejected request"
                )

                print(
                    response.text[:300]
                )

                return None


            response.raise_for_status()

            return response.json()


        except Exception as e:

            print(
                f"Attempt {attempt+1} failed:",
                e
            )

            time.sleep(3)


    return None




def check_url(url):

    if not url:
        return False


    try:

        r = requests.get(
            url,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            },
            timeout=10,
            stream=True
        )


        return r.status_code == 200


    except:

        return False




def get_stream(item):

    return (
        item.get("url")
        or item.get("stream")
        or item.get("stream_url")
        or item.get("m3u8")
        or ""
    )




def validate(item):

    name = item.get(
        "name",
        "Unknown"
    )

    logo = item.get(
        "logo",
        ""
    )

    stream = get_stream(item)


    if not stream:
        return None


    if not check_url(stream):
        return None



    return {

        "name": name,

        "logo": logo,

        "group":
            item.get(
                "group",
                "OTTPLUS"
            ),

        "stream": stream

    }




def fetch_channels():


    if not API_URL:

        raise Exception(
            "API_URL_ottplus missing"
        )


    print(
        "Downloading API data..."
    )


    data = request_api(
        API_URL
    )


    if data is None:

        raise Exception(
            "API request failed"
        )


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



    print(
        "Total channels:",
        len(data)
    )


    return data




def create_m3u(channels):


    print(
        "Checking streams..."
    )


    working = []


    with ThreadPoolExecutor(
        max_workers=20
    ) as executor:


        jobs = [

            executor.submit(
                validate,
                ch
            )

            for ch in channels

        ]


        for job in as_completed(jobs):

            result = job.result()

            if result:

                working.append(result)



    # remove duplicate

    unique = {}

    for ch in working:

        unique[
            ch["stream"]
        ] = ch



    working = list(
        unique.values()
    )



    working.sort(
        key=lambda x:
        x["name"].lower()
    )



    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:


        f.write(
            "#EXTM3U\n"
        )


        for ch in working:


            f.write(

                f'#EXTINF:-1 '
                f'tvg-name="{ch["name"]}" '
                f'tvg-logo="{ch["logo"]}" '
                f'group-title="{ch["group"]}",'
                f'{ch["name"]}\n'

            )


            f.write(
                ch["stream"]
                + "\n"
            )



    print(
        "Created:",
        OUTPUT_FILE
    )

    print(
        "Working:",
        len(working)
    )




def main():


    channels = fetch_channels()

    create_m3u(
        channels
    )



if __name__ == "__main__":

    main()

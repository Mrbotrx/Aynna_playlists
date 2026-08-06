import os
import requests
import time


API_URL = os.getenv("API_URL_ottplus")
API_KEY = os.getenv("API_KEY")


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}


if API_KEY:
    HEADERS["Authorization"] = f"Bearer {API_KEY}"


def fetch_api():

    if not API_URL:
        raise Exception(
            "Missing API_URL_ottplus secret"
        )


    for attempt in range(3):

        print(
            f"API request attempt {attempt+1}"
        )


        try:

            r = requests.get(
                API_URL,
                headers=HEADERS,
                timeout=30
            )


            print(
                "Status:",
                r.status_code
            )


            if r.status_code == 403:

                print(
                    "Server blocked GitHub Actions IP"
                )

                print(
                    r.text[:200]
                )

                raise Exception(
                    "API access forbidden"
                )


            r.raise_for_status()


            return r.json()


        except requests.exceptions.RequestException as e:

            print(e)

            time.sleep(5)


    raise Exception(
        "API failed after retries"
    )

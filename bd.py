# bd.py

import requests

API = "https://www.btvlive.gov.bd/api/home"

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(API, headers=headers, timeout=15)
r.raise_for_status()

data = r.json()

print("#EXTM3U")

def find_streams(obj):
    if isinstance(obj, dict):
        name = obj.get("name") or obj.get("title") or obj.get("channel_name")
        url = obj.get("m3u8") or obj.get("stream_url") or obj.get("url")

        if name and url and ".m3u8" in url:
            print(f'#EXTINF:-1,{name}')
            print(url)

        for v in obj.values():
            find_streams(v)

    elif isinstance(obj, list):
        for item in obj:
            find_streams(item)

find_streams(data)

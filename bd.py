import requests

API = "https://www.btvlive.gov.bd/api/home"
OUTPUT = "bdt.m3u8"

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(API, headers=headers, timeout=30)
r.raise_for_status()

data = r.json()

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n\n")

    channels = data.get("channel_list", [])

    for ch in channels:
        name = ch.get("channel_name", "BTV")
        url = ch.get("count_url", "").strip()

        if ".m3u8" in url:
            f.write(f'#EXTINF:-1 tvg-name="{name}",{name}\n')
            f.write(url + "\n\n")

print(f"Created {OUTPUT}")

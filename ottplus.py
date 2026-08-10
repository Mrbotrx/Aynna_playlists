import os
import json
import requests
from pathlib import Path
from html import escape


# ============================================================
# CONFIG
# ============================================================

# API URL এখানে লিখবেন না।
# Environment variable থেকে নেওয়া হবে।
API_URL = os.getenv("OTTPLUS_API_URL")

OUTPUT_FILE = "ottplus.m3u8"
JSON_BACKUP = "ottplus.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}


# ============================================================
# FETCH API
# ============================================================

def fetch_api():
    if not API_URL:
        raise RuntimeError(
            "OTTPLUS_API_URL environment variable is not set."
        )

    response = requests.get(
        API_URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# FIND LOGO
# ============================================================

def get_logo(content):
    logo_fields = [
        "tv_cover",
        "thumbnail",
        "thumbnail_background",
        "poster",
        "poster_background",
        "lg_image",
        "sm_image",
    ]

    for field in logo_fields:
        value = content.get(field)

        if value:
            return str(value)

    return ""


# ============================================================
# EXTRACT CHANNELS
# ============================================================

def extract_channels(data):

    channels = []
    seen_urls = set()

    result = data.get("result", {})

    sections = result.get("sections", [])

    if not isinstance(sections, list):
        return channels

    for section in sections:

        items = section.get("items", [])

        if not isinstance(items, list):
            continue

        for item in items:

            content = item.get("content")

            if not isinstance(content, dict):
                continue

            stream_url = content.get("url")

            if not stream_url:
                continue

            stream_url = str(stream_url).strip()

            # Remove duplicate streams
            if stream_url in seen_urls:
                continue

            seen_urls.add(stream_url)

            name = (
                content.get("title")
                or item.get("title")
                or "Unknown Channel"
            )

            name = str(name).strip()

            logo = get_logo(content)

            channel_id = (
                content.get("id")
                or item.get("content_id")
                or ""
            )

            channel_type = (
                content.get("type")
                or "live-tvs"
            )

            channels.append({
                "id": str(channel_id),
                "name": name,
                "logo": logo,
                "url": stream_url,
                "type": str(channel_type),
            })

    return channels


# ============================================================
# ESCAPE M3U ATTRIBUTE
# ============================================================

def clean_attribute(value):
    value = str(value or "")

    return (
        value
        .replace('"', "'")
        .replace("\r", "")
        .replace("\n", " ")
    )


# ============================================================
# CREATE M3U8
# ============================================================

def create_m3u(channels):

    lines = [
        "#EXTM3U"
    ]

    for channel in channels:

        channel_id = clean_attribute(channel["id"])
        name = clean_attribute(channel["name"])
        logo = clean_attribute(channel["logo"])
        url = channel["url"]

        extinf = (
            '#EXTINF:-1 '
            f'tvg-id="{channel_id}" '
            f'tvg-name="{name}" '
            f'tvg-logo="{logo}" '
            'group-title="OTTPlus",'
            f'{name}'
        )

        lines.append(extinf)
        lines.append(url)

    return "\n".join(lines) + "\n"


# ============================================================
# SAVE M3U8
# ============================================================

def save_playlist(content):

    Path(OUTPUT_FILE).write_text(
        content,
        encoding="utf-8"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("================================")
    print(" OTTPlus Live TV M3U Generator")
    print("================================")

    try:

        print("[1] Fetching API...")

        data = fetch_api()

        # Save JSON locally.
        # চাইলে এই অংশটি remove করতে পারেন।
        Path(JSON_BACKUP).write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

        print("[2] Extracting channels...")

        channels = extract_channels(data)

        if not channels:
            print("[!] No channels found.")
            return

        print(f"[+] Channels found: {len(channels)}")

        print("[3] Creating M3U8...")

        playlist = create_m3u(channels)

        save_playlist(playlist)

        print()
        print("================================")
        print(f"Done: {OUTPUT_FILE}")
        print(f"Channels: {len(channels)}")
        print("================================")
        print()

        for number, channel in enumerate(channels, 1):
            print(
                f"{number:03d}. "
                f"{channel['name']} -> "
                f"{channel['url']}"
            )

    except requests.exceptions.Timeout:
        print("[ERROR] API request timed out.")

    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP error: {e}")

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API request failed: {e}")

    except json.JSONDecodeError:
        print("[ERROR] API did not return valid JSON.")

    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()

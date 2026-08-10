import os
import sys
import json
import requests
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

API_URL = os.getenv("OTTPLUS_API_URL")

OUTPUT_FILE = Path("ottplus.m3u8")

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
            "OTTPLUS_API_URL GitHub Secret/Environment Variable is missing."
        )

    print("Fetching API...")

    response = requests.get(
        API_URL,
        headers=HEADERS,
        timeout=30
    )

    print("HTTP Status:", response.status_code)

    response.raise_for_status()

    return response.json()


# ============================================================
# LOGO
# ============================================================

def get_logo(content):

    for field in [
        "tv_cover",
        "thumbnail",
        "thumbnail_background",
        "poster",
        "poster_background",
    ]:

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
        raise RuntimeError(
            "API response does not contain result.sections"
        )

    print("Sections:", len(sections))

    for section in sections:

        section_title = section.get("title", "")

        items = section.get("items", [])

        if not isinstance(items, list):
            continue

        print(
            f"Section: {section_title} | "
            f"Items: {len(items)}"
        )

        for item in items:

            content = item.get("content")

            if not isinstance(content, dict):
                continue

            stream_url = content.get("url")

            if not stream_url:
                continue

            stream_url = str(stream_url).strip()

            # Duplicate check
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

            channels.append({
                "id": str(channel_id),
                "name": name,
                "logo": logo,
                "url": stream_url,
            })

    return channels


# ============================================================
# CLEAN M3U TEXT
# ============================================================

def clean_text(value):

    return (
        str(value or "")
        .replace('"', "'")
        .replace("\r", "")
        .replace("\n", " ")
        .strip()
    )


# ============================================================
# CREATE M3U8
# ============================================================

def create_m3u(channels):

    lines = [
        "#EXTM3U"
    ]

    for channel in channels:

        channel_id = clean_text(channel["id"])
        name = clean_text(channel["name"])
        logo = clean_text(channel["logo"])
        url = channel["url"]

        lines.append(
            '#EXTINF:-1 '
            f'tvg-id="{channel_id}" '
            f'tvg-name="{name}" '
            f'tvg-logo="{logo}" '
            'group-title="OTTPlus",'
            f'{name}'
        )

        lines.append(url)

    return "\n".join(lines) + "\n"


# ============================================================
# MAIN
# ============================================================

def main():

    print("==========================================")
    print("       OTTPlus M3U8 Generator")
    print("==========================================")

    try:

        # ------------------------------------
        # API
        # ------------------------------------

        data = fetch_api()

        # ------------------------------------
        # Basic API validation
        # ------------------------------------

        if data.get("success") is False:
            raise RuntimeError(
                f"API returned success=false: "
                f"{data.get('message', 'Unknown error')}"
            )

        # ------------------------------------
        # Extract
        # ------------------------------------

        channels = extract_channels(data)

        print()
        print("Channels found:", len(channels))

        if not channels:
            raise RuntimeError(
                "No live TV channels found in API response."
            )

        # ------------------------------------
        # Create playlist
        # ------------------------------------

        playlist = create_m3u(channels)

        OUTPUT_FILE.write_text(
            playlist,
            encoding="utf-8"
        )

        # ------------------------------------
        # Verify file
        # ------------------------------------

        if not OUTPUT_FILE.exists():
            raise RuntimeError(
                "Playlist file was not created."
            )

        file_size = OUTPUT_FILE.stat().st_size

        if file_size == 0:
            raise RuntimeError(
                "Playlist file is empty."
            )

        print()
        print("==========================================")
        print("SUCCESS")
        print("==========================================")
        print("Output:", OUTPUT_FILE)
        print("Channels:", len(channels))
        print("Size:", file_size, "bytes")
        print("==========================================")

        print()
        print("Channels:")

        for i, channel in enumerate(channels, 1):

            print(
                f"{i}. {channel['name']}"
            )

        return 0

    except requests.exceptions.Timeout:

        print(
            "ERROR: API request timed out.",
            file=sys.stderr
        )

        return 1

    except requests.exceptions.HTTPError as e:

        print(
            f"ERROR: HTTP request failed: {e}",
            file=sys.stderr
        )

        return 1

    except requests.exceptions.RequestException as e:

        print(
            f"ERROR: Network/API error: {e}",
            file=sys.stderr
        )

        return 1

    except json.JSONDecodeError:

        print(
            "ERROR: API did not return valid JSON.",
            file=sys.stderr
        )

        return 1

    except Exception as e:

        print(
            f"ERROR: {e}",
            file=sys.stderr
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())

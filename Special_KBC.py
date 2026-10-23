
#!/usr/bin/env python3

import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from html.parser import HTMLParser

import requests

SOURCE_URL = "https://www.bhoomtv.org/channel/bengali/"
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "Special_KBC.m3u"
DEBUG_FILE = BASE_DIR / "extract_debug.txt"
TIMEOUT = 30

EXTENSIONS = {
    ".m3u", ".m3u8", ".mp4", ".mp3", ".mpd",
    ".ts", ".webm", ".m4v", ".m4a", ".aac",
    ".ogg", ".oga", ".wav", ".jpg", ".jpeg",
    ".png", ".gif", ".webp", ".avif", ".svg"
}

URL_PATTERN = re.compile(
    r"""(?i)(?:https?:)?//[^\s"'<>\\]+"""
    r"""|(?:/|\./|\.\./)[^\s"'<>\\]+"""
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SpecialKBC/1.0)",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}


def normalize_url(raw, base_url):
    raw = html.unescape(str(raw)).strip().strip("'\"")
    raw = raw.replace("\\/", "/")

    if not raw or raw.startswith(
        ("data:", "javascript:", "blob:", "#")
    ):
        return None

    url = urljoin(base_url, raw)
    parts = urlsplit(url)

    if parts.scheme not in ("http", "https") or not parts.hostname:
        return None

    return url


def is_media_url(url):
    parts = urlsplit(url)
    path = parts.path.lower()

    if Path(path).suffix in EXTENSIONS:
        return True

    # Some public endpoints expose a playlist without a file extension.
    query = parts.query.lower()
    return any(
        marker in query
        for marker in ("format=m3u8", "type=m3u8", "format=mp4")
    )


class PageParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.urls = set()
        self.debug_urls = set()
        self.channel_names = []

    def inspect(self, value):
        if not value:
            return

        value = html.unescape(str(value))
        value = value.replace("\\/", "/")

        for match in URL_PATTERN.findall(value):
            url = normalize_url(match.rstrip("),;]}"), self.base_url)

            if not url:
                continue

            self.debug_urls.add(url)

            if is_media_url(url):
                self.urls.add(url)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        for key in (
            "src", "href", "poster", "data-src",
            "data-url", "data-video", "data-stream"
        ):
            self.inspect(attrs.get(key))

        self.inspect(json.dumps(attrs, ensure_ascii=False))

    def handle_data(self, data):
        self.inspect(data)


def write_playlist(urls):
    with OUTPUT_FILE.open("w", encoding="utf-8", newline="\n") as file:
        file.write("#EXTM3U\n")

        for url in sorted(urls):
            file.write(url + "\n")


def main():
    # Ensure the output exists before network operations.
    try:
        write_playlist([])
    except OSError as exc:
        print(f"[ERROR] Cannot create playlist: {exc}")
        return 1

    debug = []
    media_urls = set()

    try:
        print(f"[INFO] Fetching {SOURCE_URL}")

        response = requests.get(
            SOURCE_URL,
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        response.raise_for_status()

        print(f"[INFO] HTTP status: {response.status_code}")
        print(f"[INFO] Content-Type: {response.headers.get('Content-Type')}")
        print(f"[INFO] HTML size: {len(response.text)} bytes")

        parser = PageParser(response.url)
        parser.feed(response.text)
        parser.close()

        media_urls.update(parser.urls)

        debug.append(f"Final URL: {response.url}")
        debug.append(f"HTTP status: {response.status_code}")
        debug.append(f"HTML size: {len(response.text)}")
        debug.append(f"Media URLs found: {len(media_urls)}")
        debug.append("")
        debug.append("Discovered URLs:")
        debug.extend(sorted(parser.debug_urls))

        write_playlist(media_urls)

        print(f"[OK] Media URLs: {len(media_urls)}")
        print(f"[OK] Playlist: {OUTPUT_FILE}")

        if not media_urls:
            print(
                "[WARN] No media URLs found in static HTML. "
                "The player may load sources from another endpoint."
            )

    except requests.RequestException as exc:
        debug.append(f"Request error: {exc}")
        print(f"[ERROR] Request failed: {exc}")
        # Keep the existing valid, empty playlist.

    except Exception as exc:
        debug.append(f"Extraction error: {exc}")
        print(f"[ERROR] Extraction failed: {exc}")
        return 1

    try:
        DEBUG_FILE.write_text(
            "\n".join(debug) + "\n",
            encoding="utf-8",
        )
        print(f"[INFO] Debug log: {DEBUG_FILE}")
    except OSError as exc:
        print(f"[WARN] Could not write debug log: {exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

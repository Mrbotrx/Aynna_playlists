
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import html
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from html.parser import HTMLParser

import requests

SOURCE_URL = "https://www.bhoomtv.org/channel/bengali/"
OUTPUT_FILE = Path(__file__).resolve().parent / "Special_KBC.m3u"
TIMEOUT = 30

MEDIA_EXTENSIONS = {
    ".m3u", ".m3u8", ".mp4", ".mp3", ".m4v",
    ".webm", ".ts", ".mpd", ".m4a", ".aac",
    ".ogg", ".oga", ".wav", ".flac", ".mpg",
    ".mpeg", ".mov", ".avi", ".wmv", ".jpg",
    ".jpeg", ".png", ".gif", ".webp", ".avif",
    ".bmp", ".svg", ".ico", ".tif", ".tiff",
    ".heic", ".jfif", ".jpe", ".mp2", ".opus"
}

URL_PATTERN = re.compile(
    r"""(?i)(?:https?:)?//[^\s"'<>\\]+|"""
    r"""(?:/|\./|\.\./)[^\s"'<>\\]+"""
)


class MediaParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.urls = set()

    def add_url(self, value):
        if not value:
            return

        value = html.unescape(value.strip()).strip("'\"")
        value = value.replace("\\/", "/")

        if not value or value.startswith(
            ("data:", "javascript:", "blob:", "#")
        ):
            return

        if value.startswith("//"):
            value = "https:" + value

        url = urljoin(self.base_url, value)
        parts = urlsplit(url)

        if parts.scheme not in ("http", "https"):
            return

        if not parts.hostname:
            return

        extension = Path(parts.path.lower()).suffix

        if extension in MEDIA_EXTENSIONS:
            self.urls.add(url)

    def scan_text(self, text):
        if not text:
            return

        text = html.unescape(text)
        text = text.replace("\\/", "/")

        for match in URL_PATTERN.findall(text):
            self.add_url(match.rstrip("),;]}"))

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if not value:
                continue

            key = key.lower()

            if key in {
                "src", "href", "poster", "data-src",
                "data-url", "data-video", "content"
            }:
                self.add_url(value)

            # srcset may contain multiple image URLs.
            if key == "srcset":
                for item in value.split(","):
                    candidate = item.strip().split()
                    if candidate:
                        self.add_url(candidate[0])

            self.scan_text(value)

    def handle_data(self, data):
        # Includes ordinary text and inline script contents.
        self.scan_text(data)


def write_playlist(urls):
    """Always write a valid M3U header, even if no URLs were found."""
    with OUTPUT_FILE.open("w", encoding="utf-8", newline="\n") as file:
        file.write("#EXTM3U\n")

        for url in sorted(set(urls)):
            file.write(url + "\n")


def main():
    # Create output immediately so it exists even if the request fails.
    try:
        write_playlist([])
    except OSError as error:
        print(f"[ERROR] Cannot create output file: {error}")
        return 1

    print(f"[INFO] Source: {SOURCE_URL}")
    print(f"[INFO] Output: {OUTPUT_FILE}")

    try:
        response = requests.get(
            SOURCE_URL,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; MediaURLCollector/1.0)",
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()

        parser = MediaParser(response.url)
        parser.feed(response.text)
        parser.close()

        urls = sorted(parser.urls)
        write_playlist(urls)

        print(f"[OK] HTTP status: {response.status_code}")
        print(f"[OK] URLs found: {len(urls)}")
        print(f"[OK] Playlist created: {OUTPUT_FILE.name}")

        if not urls:
            print(
                "[WARN] No matching media URLs found in the returned HTML. "
                "The player may load URLs dynamically."
            )

        return 0

    except requests.RequestException as error:
        print(f"[ERROR] Page request failed: {error}")
        # The output file already exists with a valid M3U header.
        return 0

    except (OSError, ValueError) as error:
        print(f"[ERROR] Extraction or file-writing error: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

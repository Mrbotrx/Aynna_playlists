
import re
import requests
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

SOURCE_URL = "https://www.bhoomtv.org/channel/bengali/"
OUTPUT_FILE = "Special_KBC.m3u"

EXTENSIONS = (
    ".m3u", ".m3u8", ".mp4", ".mp3",
    ".png", ".jpg", ".jpeg", ".webp",
    ".gif", ".aac", ".ogg", ".wav",
    ".webm", ".ts", ".m4a"
)

class MediaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        for key in ("src", "href", "poster", "data-src"):
            value = attrs.get(key)
            if value:
                self.add_url(value)

        for value in attrs.values():
            if isinstance(value, str):
                self.scan_text(value)

    def handle_data(self, data):
        self.scan_text(data)

    def add_url(self, value):
        value = value.strip().strip("'\"")
        if not value or value.startswith(("data:", "javascript:")):
            return

        url = urljoin(SOURCE_URL, value)
        parts = urlsplit(url)

        if parts.scheme not in ("http", "https"):
            return

        path = parts.path.lower()
        if path.endswith(EXTENSIONS):
            self.urls.add(url)

    def scan_text(self, text):
        pattern = r"""(?i)(?:https?:)?//[^\s"'<>\\]+|(?:/|\./|\.\./)[^\s"'<>\\]+"""
        for match in re.findall(pattern, text):
            self.add_url(match.rstrip("),;]"))


def main():
    print("[*] Fetching page...")

    try:
        response = requests.get(
            SOURCE_URL,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20
        )
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"[!] Request failed: {error}")
        return

    parser = MediaParser()
    parser.feed(response.text)

    urls = sorted(parser.urls)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write("#EXTM3U\n")
        for url in urls:
            file.write(url + "\n")

    print(f"[+] Found: {len(urls)} public media URLs")
    print(f"[+] Saved to: {OUTPUT_FILE}")
    print("[i] Dynamic player URLs may not appear in static HTML.")


if __name__ == "__main__":
    main()

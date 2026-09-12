import os
import re
import requests
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed


# =========================================================
# CONFIG
# =========================================================

API_URL = os.environ.get("AYNAOTT_API_URL")

OUTPUT_DIR = "output"
PLAYLIST_FILE = os.path.join(
    OUTPUT_DIR,
    "aynnaott.m3u8"
)

MAX_WORKERS = 20
CONNECT_TIMEOUT = 5
READ_TIMEOUT = 5
MAX_PLAYLIST_BYTES = 200000

os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================================================
# ⭐ ALWAYS KEEP CHANNEL
# =========================================================

ALWAYS_CHANNEL = {
    "name": "IPTV LINKS",

    "url": (
        "https://github.com/Mrbotrx/Mrbotrx/raw/"
        "refs/heads/main/IPTV_LINKS_VIDEO.mp4"
    ),

    "logo": (
        "https://raw.githubusercontent.com/Mrbotrx/"
        "Mrbotrx/refs/heads/main/IPTV_LINKS_LOGO.jpg"
    ),

    "group": "IPTV"
}


# =========================================================
# HTTP HEADERS
# =========================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Connection": "keep-alive"
}


# =========================================================
# CATEGORY RULES
# =========================================================

CATEGORY_RULES = {

    "Sports": [
        "sport", "sports", "espn",
        "star sports", "ten sports",
        "sony sports", "bein sports",
        "bt sport", "sky sport",
        "supersport", "cricket",
        "football", "soccer", "fifa",
        "tennis", "wwe", "ufc",
        "nba", "nfl", "olympic"
    ],

    "News": [
        "news", "cnn", "bbc news",
        "al jazeera", "reuters",
        "ndtv", "abp news",
        "india today", "times now",
        "republic", "zee news",
        "news18", "news 18",
        "somoy", "jamuna",
        "ekattor", "channel 24",
        "ntv", "dbc", "atn news",
        "independent"
    ],

    "Movies": [
        "movie", "movies",
        "cinema", "film", "films",
        "hbo", "star movies",
        "sony max", "sony pix",
        "zee cinema",
        "and pictures",
        "bollywood", "hollywood"
    ],

    "Kids": [
        "kids", "cartoon",
        "cartoons", "nick",
        "nickelodeon", "disney",
        "disney junior", "pogo",
        "hungama", "sonic",
        "baby", "toons"
    ],

    "Documentary": [
        "documentary",
        "discovery",
        "nat geo",
        "national geographic",
        "history", "animal planet",
        "science", "bbc earth"
    ],

    "Music": [
        "music", "songs",
        "mtv", "vh1",
        "9xm", "9x music",
        "mastiii", "b4u music",
        "zoom"
    ],

    "Lifestyle": [
        "lifestyle", "food",
        "cooking", "travel",
        "fashion", "fashion tv",
        "home", "living", "tlc"
    ],

    "Bangla": [
        "bangla",
        "বাংলা",
        "bangladesh",
        "somoy",
        "jamuna",
        "ekattor",
        "ntv",
        "channel i",
        "channel-i",
        "atn",
        "dbc",
        "independent tv",
        "banglavision",
        "bangla vision",
        "boishakhi",
        "my tv",
        "gazi tv",
        "gtv"
    ],

    "Hindi": [
        "hindi",
        "star plus",
        "colors",
        "sony sab",
        "sony entertainment",
        "zee tv",
        "zee cinema",
        "and tv",
        "sab tv"
    ],

    "International": [
        "international",
        "global",
        "world",
        "english",
        "bbc",
        "cnn",
        "al jazeera",
        "france 24",
        "dw",
        "euronews"
    ],

    "Entertainment": [
        "entertainment",
        "comedy",
        "zee",
        "colors",
        "star plus",
        "sony",
        "sab"
    ]
}


# =========================================================
# CATEGORY ORDER
# =========================================================

CATEGORY_ORDER = [
    "News",
    "Sports",
    "Movies",
    "Entertainment",
    "Music",
    "Kids",
    "Documentary",
    "Lifestyle",
    "Bangla",
    "Hindi",
    "International",
    "IPTV"
]


# =========================================================
# TEXT CLEAN
# =========================================================

def clean_text(value):

    if value is None:
        return ""

    value = str(value).lower()

    value = value.replace("_", " ")
    value = value.replace("-", " ")

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# =========================================================
# FIND URL
# =========================================================

def is_url(value):

    if not isinstance(value, str):
        return False

    value = value.strip().lower()

    return (
        value.startswith("http://")
        or value.startswith("https://")
    )


# =========================================================
# FIND LOGO FROM OBJECT
# =========================================================

def find_logo(data):

    if not isinstance(data, dict):
        return ""


    # Most common logo fields
    logo_fields = [

        "logo",
        "logoUrl",
        "logoURL",
        "logo_url",

        "channelLogo",
        "channelLogoUrl",
        "channel_logo",
        "channel_logo_url",

        "image",
        "imageUrl",
        "imageURL",
        "image_url",

        "thumbnail",
        "thumbnailUrl",
        "thumbnailURL",

        "icon",
        "iconUrl",
        "iconURL",

        "poster",
        "posterUrl",

        "picture",
        "pictureUrl",

        "avatar",
        "avatarUrl",

        "cover",
        "coverUrl",

        "artwork",
        "artworkUrl"
    ]


    # Direct fields
    for field in logo_fields:

        value = data.get(field)

        if is_url(value):
            return value.strip()


    # -----------------------------------------------------
    # Nested logo object
    # -----------------------------------------------------

    for field in [
        "logos",
        "logo",
        "image",
        "images",
        "artwork"
    ]:

        value = data.get(field)


        if isinstance(value, dict):

            for sub_key in [
                "url",
                "src",
                "href",
                "original",
                "large",
                "medium",
                "small"
            ]:

                sub_value = value.get(sub_key)

                if is_url(sub_value):
                    return sub_value.strip()


        elif isinstance(value, list):

            for item in value:

                if is_url(item):
                    return item.strip()


                if isinstance(item, dict):

                    for sub_key in [
                        "url",
                        "src",
                        "href",
                        "original",
                        "large",
                        "medium",
                        "small"
                    ]:

                        sub_value = item.get(
                            sub_key
                        )

                        if is_url(sub_value):
                            return sub_value.strip()


    return ""


# =========================================================
# FIND CHANNEL NAME
# =========================================================

def find_channel_name(
    data,
    fallback="Unknown"
):

    if not isinstance(data, dict):
        return fallback


    fields = [

        "name",
        "channelName",
        "channel_name",
        "title",
        "displayName",
        "display_name",
        "channel",
        "stationName",
        "station_name"
    ]


    for field in fields:

        value = data.get(field)


        if isinstance(value, str):

            value = value.strip()

            if value:
                return value


    return fallback


# =========================================================
# FIND CATEGORY FROM API
# =========================================================

def find_api_category(data):

    if not isinstance(data, dict):
        return ""


    fields = [

        "category",
        "categoryName",
        "category_name",

        "group",
        "groupName",
        "group_name",

        "genre",
        "genreName",
        "genre_name",

        "type",
        "channelType",
        "channel_type",

        "section",
        "sectionName"
    ]


    values = []


    for field in fields:

        value = data.get(field)


        if isinstance(value, str):

            if value.strip():
                values.append(
                    value.strip()
                )


        elif isinstance(value, list):

            for item in value:

                if isinstance(item, str):
                    values.append(item.strip())


                elif isinstance(item, dict):

                    for sub in [
                        "name",
                        "title",
                        "label"
                    ]:

                        if isinstance(
                            item.get(sub),
                            str
                        ):

                            values.append(
                                item[sub].strip()
                            )


        elif isinstance(value, dict):

            for sub in [
                "name",
                "title",
                "label"
            ]:

                if isinstance(
                    value.get(sub),
                    str
                ):

                    values.append(
                        value[sub].strip()
                    )


    return " ".join(values)


# =========================================================
# AUTO CATEGORY
# =========================================================

def auto_category(
    name="",
    api_category=""
):

    name_text = clean_text(name)

    category_text = clean_text(
        api_category
    )

    combined = (
        name_text
        + " "
        + category_text
    ).strip()


    # -----------------------------------------------------
    # REMOVE RELIGION
    # -----------------------------------------------------

    religion_words = [
        "religion",
        "religious",
        "worship",
        "church",
        "islamic",
        "islam",
        "hindu",
        "christian",
        "quran",
        "koran"
    ]


    if any(
        word in combined
        for word in religion_words
    ):

        return "IPTV"


    # -----------------------------------------------------
    # SEARCH CATEGORY
    # -----------------------------------------------------

    priority = [
        "Sports",
        "News",
        "Movies",
        "Kids",
        "Documentary",
        "Music",
        "Bangla",
        "Hindi",
        "Lifestyle",
        "Entertainment",
        "International"
    ]


    for category in priority:

        for keyword in CATEGORY_RULES.get(
            category,
            []
        ):

            keyword = clean_text(
                keyword
            )


            if not keyword:
                continue


            # Word-based match for short words
            if len(keyword) <= 3:

                pattern = (
                    r"\b"
                    + re.escape(keyword)
                    + r"\b"
                )

                if re.search(
                    pattern,
                    combined
                ):
                    return category

            else:

                if keyword in combined:
                    return category


    # -----------------------------------------------------
    # API CATEGORY
    # -----------------------------------------------------

    if category_text:

        api_category_clean = (
            category_text.strip()
        )


        if api_category_clean:

            return api_category_clean.title()


    # -----------------------------------------------------
    # NOTHING FOUND
    # -----------------------------------------------------
    # IMPORTANT:
    # If category cannot be found,
    # it ALWAYS goes to IPTV.

    return "IPTV"


# =========================================================
# FETCH API
# =========================================================

def fetch_api():

    if not API_URL:

        raise Exception(
            "AYNAOTT_API_URL is missing"
        )


    print(
        "Fetching AYNNA OTT API..."
    )


    response = requests.get(
        API_URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        },
        timeout=15
    )


    response.raise_for_status()


    return response.json()


# =========================================================
# RECURSIVE CHANNEL FINDER
# =========================================================

def find_channels(
    data,
    channels=None,
    parent_name="Unknown",
    parent_logo="",
    parent_category=""
):

    if channels is None:
        channels = []


    # =====================================================
    # DICT
    # =====================================================

    if isinstance(data, dict):

        current_name = find_channel_name(
            data,
            parent_name
        )


        current_logo = (
            find_logo(data)
            or parent_logo
        )


        current_api_category = (
            find_api_category(data)
            or parent_category
        )


        current_group = auto_category(
            current_name,
            current_api_category
        )


        # -------------------------------------------------
        # Search ALL string fields for M3U8
        # -------------------------------------------------

        for key, value in data.items():

            if not isinstance(
                value,
                str
            ):
                continue


            urls = re.findall(
                r'https?://[^\s"\'<>]+?\.m3u8(?:\?[^\s"\'<>]*)?',
                value,
                re.IGNORECASE
            )


            for stream_url in urls:

                channels.append(
                    {
                        "name": current_name,

                        "url": stream_url.strip(),

                        "logo": current_logo,

                        "group": current_group
                    }
                )


        # -------------------------------------------------
        # Recursive objects
        # -------------------------------------------------

        for value in data.values():

            if isinstance(
                value,
                (dict, list)
            ):

                find_channels(
                    value,
                    channels,
                    current_name,
                    current_logo,
                    current_api_category
                )


    # =====================================================
    # LIST
    # =====================================================

    elif isinstance(data, list):

        for item in data:

            find_channels(
                item,
                channels,
                parent_name,
                parent_logo,
                parent_category
            )


    return channels


# =========================================================
# REMOVE DUPLICATE
# =========================================================

def remove_duplicate(
    channels
):

    result = []

    seen = set()


    for channel in channels:

        url = channel.get(
            "url",
            ""
        ).strip()


        if not url:
            continue


        key = url.lower()


        if key in seen:
            continue


        seen.add(key)


        name = (
            channel.get(
                "name",
                "Unknown"
            )
            or "Unknown"
        )


        logo = (
            channel.get(
                "logo",
                ""
            )
            or ""
        )


        group = auto_category(
            name,
            channel.get(
                "group",
                ""
            )
        )


        result.append(
            {
                "name": name.strip(),

                "url": url,

                "logo": logo.strip(),

                "group": group
            }
        )


    return result


# =========================================================
# VALIDATE M3U8
# =========================================================

def validate_m3u8_content(
    response
):

    try:

        content_type = (
            response.headers.get(
                "Content-Type",
                ""
            )
            .lower()
        )


        content = response.raw.read(
            MAX_PLAYLIST_BYTES
        )


        if not content:
            return False


        text = content.decode(
            "utf-8",
            errors="ignore"
        )


        text_upper = text.upper()


        if "#EXTM3U" in text_upper:
            return True


        if "#EXT-X-STREAM-INF" in text_upper:
            return True


        if "#EXTINF" in text_upper:
            return True


        if "#EXT-X-TARGETDURATION" in text_upper:
            return True


        if (
            "mpegurl" in content_type
            or "m3u8" in content_type
        ):
            return True


    except Exception:
        pass


    return False


# =========================================================
# CHECK ONE STREAM
# =========================================================

def check_one_channel(
    channel
):

    url = channel.get(
        "url",
        ""
    )


    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=(
                CONNECT_TIMEOUT,
                READ_TIMEOUT
            ),
            stream=True,
            allow_redirects=True
        )


        if response.status_code != 200:

            response.close()

            return None


        valid = validate_m3u8_content(
            response
        )


        response.close()


        if not valid:
            return None


        return channel


    except Exception:

        return None


# =========================================================
# CHECK WORKING CHANNELS
# =========================================================

def check_working_channels(
    channels
):

    working = []


    print(
        "\nChecking M3U8 channels..."
    )


    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = [
            executor.submit(
                check_one_channel,
                channel
            )
            for channel in channels
        ]


        for future in as_completed(
            futures
        ):

            try:

                result = future.result()


                if result:

                    working.append(
                        result
                    )


            except Exception:
                pass


    return working


# =========================================================
# ⭐ ALWAYS ADD IPTV LINKS
# =========================================================

def add_always_channel(
    channels
):

    always_url = ALWAYS_CHANNEL[
        "url"
    ].lower()


    # Remove duplicate fixed URL
    channels = [
        channel
        for channel in channels
        if channel.get(
            "url",
            ""
        ).lower() != always_url
    ]


    # ALWAYS append
    channels.append(
        ALWAYS_CHANNEL.copy()
    )


    return channels


# =========================================================
# SORT
# =========================================================

def sort_channels(
    channels
):

    def sort_key(channel):

        category = channel.get(
            "group",
            "IPTV"
        )


        try:

            category_index = (
                CATEGORY_ORDER.index(
                    category
                )
            )

        except ValueError:

            category_index = 999


        return (
            category_index,
            channel.get(
                "name",
                ""
            ).lower()
        )


    return sorted(
        channels,
        key=sort_key
    )


# =========================================================
# M3U ESCAPE
# =========================================================

def m3u_escape(
    value
):

    if value is None:
        return ""


    value = str(value)

    value = value.replace(
        '"',
        "'"
    )

    value = value.replace(
        "\n",
        " "
    )

    value = value.replace(
        "\r",
        " "
    )

    return value.strip()


# =========================================================
# CREATE PLAYLIST
# =========================================================

def create_playlist(
    channels
):

    channels = sort_channels(
        channels
    )


    total = len(
        channels
    )


    updated = datetime.now(
        timezone.utc
    ).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )


    with open(
        PLAYLIST_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        # =================================================
        # HEADER
        # =================================================

        file.write(
            "#EXTM3U\n"
        )

        file.write(
            "# 📺 AYNNA OTT IPTV PLAYLIST\n"
        )

        file.write(
            f"# #️⃣ Total Channels: {total}\n"
        )

        file.write(
            f"# 🕒 Updated: {updated}\n"
        )

        file.write(
            "# ⚡ Working Channels Only\n"
        )

        file.write(
            "# 🔥 Auto Category & Logo\n"
        )

        file.write(
            "# 📡 M3U8 Playlist\n"
        )

        file.write(
            "# ⭐ IPTV LINKS Always Included\n"
        )

        file.write(
            "#\n"
        )


        current_category = None


        # =================================================
        # CHANNELS
        # =================================================

        for channel in channels:

            name = m3u_escape(
                channel.get(
                    "name",
                    "Unknown"
                )
            )


            logo = m3u_escape(
                channel.get(
                    "logo",
                    ""
                )
            )


            group = m3u_escape(
                channel.get(
                    "group",
                    "IPTV"
                )
            )


            url = channel.get(
                "url",
                ""
            ).strip()


            # -------------------------------------------------
            # CATEGORY HEADER
            # -------------------------------------------------

            if group != current_category:

                file.write(
                    f"# ===== {group} =====\n"
                )

                current_category = group


            # -------------------------------------------------
            # EXTINF
            # -------------------------------------------------

            file.write(
                f'#EXTINF:-1 '
                f'tvg-id="" '
                f'tvg-name="{name}" '
                f'tvg-logo="{logo}" '
                f'group-title="{group}",'
                f'{name}\n'
            )


            # -------------------------------------------------
            # URL
            # -------------------------------------------------

            file.write(
                url
                + "\n\n"
            )


    print(
        "\n======================================"
    )

    print(
        "PLAYLIST CREATED"
    )

    print(
        "======================================"
    )

    print(
        f"Total Channels: {total}"
    )

    print(
        f"File: {PLAYLIST_FILE}"
    )

    print(
        f"Updated: {updated}"
    )


# =========================================================
# CATEGORY STATS
# =========================================================

def print_stats(
    channels
):

    stats = {}


    for channel in channels:

        category = channel.get(
            "group",
            "IPTV"
        )


        stats[category] = (
            stats.get(
                category,
                0
            )
            + 1
        )


    print(
        "\nCategory Statistics:"
    )


    for category in CATEGORY_ORDER:

        if category in stats:

            print(
                f"{category}: "
                f"{stats[category]}"
            )


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "=========================================="
    )

    print(
        "AYNNA OTT IPTV AUTO GENERATOR"
    )

    print(
        "=========================================="
    )

    print(
        "✓ Working M3U8 Only"
    )

    print(
        "✓ Auto Channel Name"
    )

    print(
        "✓ Auto Logo"
    )

    print(
        "✓ Auto Category"
    )

    print(
        "✓ Unknown Category -> IPTV"
    )

    print(
        "✓ Religion Removed"
    )

    print(
        "✓ IPTV LINKS Always Included"
    )

    print(
        "=========================================="
    )


    # =====================================================
    # DEFAULT
    # =====================================================

    final_channels = []


    try:

        # -------------------------------------------------
        # 1. FETCH API
        # -------------------------------------------------

        data = fetch_api()


        # -------------------------------------------------
        # 2. FIND CHANNELS
        # -------------------------------------------------

        channels = find_channels(
            data
        )


        print(
            f"\nAPI Channels Found: "
            f"{len(channels)}"
        )


        # -------------------------------------------------
        # 3. REMOVE DUPLICATES
        # -------------------------------------------------

        channels = remove_duplicate(
            channels
        )


        print(
            f"Unique Channels: "
            f"{len(channels)}"
        )


        # -------------------------------------------------
        # 4. CHECK WORKING
        # -------------------------------------------------

        working_channels = (
            check_working_channels(
                channels
            )
        )


        print(
            f"Working API Channels: "
            f"{len(working_channels)}"
        )


        # -------------------------------------------------
        # 5. ADD FIXED CHANNEL
        # -------------------------------------------------

        final_channels = add_always_channel(
            working_channels
        )


    except Exception as error:

        print(
            f"\nAPI ERROR: {error}"
        )


        # -------------------------------------------------
        # IMPORTANT:
        # API fail হলেও fixed channel থাকবে
        # -------------------------------------------------

        final_channels = (
            add_always_channel([])
        )


    # =====================================================
    # FINAL CLEANUP
    # =====================================================

    final_channels = remove_duplicate(
        final_channels
    )


    # =====================================================
    # ENSURE IPTV LINKS AGAIN
    # =====================================================

    final_channels = add_always_channel(
        final_channels
    )


    # =====================================================
    # STATS
    # =====================================================

    print_stats(
        final_channels
    )


    # =====================================================
    # CREATE PLAYLIST
    # =====================================================

    create_playlist(
        final_channels
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    main()

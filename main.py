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

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# =========================================================
# ALWAYS KEEP CHANNEL
# =========================================================
# This channel will ALWAYS be included.
# It is NOT checked by the working-stream filter.

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
# AUTO CATEGORY RULES
# =========================================================

CATEGORY_RULES = {

    "Sports": [
        "sport",
        "sports",
        "espn",
        "star sports",
        "ten sports",
        "sony sports",
        "bein",
        "bt sport",
        "sky sport",
        "supersport",
        "cricket",
        "cric",
        "football",
        "soccer",
        "fifa",
        "tennis",
        "wwe",
        "ufc",
        "nba",
        "nfl",
        "olympic",
        "olympics"
    ],

    "News": [
        "news",
        "cnn",
        "bbc news",
        "al jazeera",
        "reuters",
        "ndtv",
        "abp news",
        "india today",
        "times now",
        "republic",
        "zee news",
        "news18",
        "news 18",
        "somoy",
        "jamuna",
        "ekattor",
        "channel 24",
        "ntv",
        "independent",
        "dbc",
        "atn news"
    ],

    "Movies": [
        "movie",
        "movies",
        "cinema",
        "film",
        "films",
        "hbo",
        "star movies",
        "sony max",
        "sony pix",
        "zee cinema",
        "and pictures",
        "bollywood",
        "hollywood"
    ],

    "Kids": [
        "kids",
        "cartoon",
        "cartoons",
        "nick",
        "nickelodeon",
        "disney",
        "disney junior",
        "pogo",
        "hungama",
        "sonic",
        "baby",
        "toons"
    ],

    "Documentary": [
        "documentary",
        "discovery",
        "nat geo",
        "national geographic",
        "history",
        "animal planet",
        "science",
        "bbc earth"
    ],

    "Music": [
        "music",
        "songs",
        "mtv",
        "vh1",
        "9xm",
        "9x music",
        "mastiii",
        "b4u music",
        "zoom"
    ],

    "Lifestyle": [
        "lifestyle",
        "food",
        "cooking",
        "travel",
        "fashion",
        "fashion tv",
        "home",
        "living",
        "tlc"
    ],

    "Bangla": [
        "bangla",
        "বাংলা",
        "bangladesh",
        "bd",
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
        "&tv",
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
    ],

    "IPTV": [
        "iptv",
        "live tv",
        "stream",
        "channel"
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
# CLEAN TEXT
# =========================================================

def clean_text(text):

    if not text:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"[_\-]+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# AUTO CATEGORY
# =========================================================

def auto_category(
    name="",
    api_group="",
    api_category="",
    api_genre="",
    api_type=""
):

    name_text = clean_text(
        name
    )

    supplied = clean_text(
        api_category
        or api_group
        or api_genre
        or api_type
        or ""
    )

    combined = (
        name_text
        + " "
        + supplied
    ).strip()


    # -----------------------------------------------------
    # RELIGION FILTER
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

        supplied = ""


    # -----------------------------------------------------
    # CATEGORY PRIORITY
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

        keywords = CATEGORY_RULES.get(
            category,
            []
        )


        for keyword in keywords:

            keyword = clean_text(
                keyword
            )


            if keyword and keyword in combined:

                return category


    # -----------------------------------------------------
    # API CATEGORY
    # -----------------------------------------------------

    if supplied:

        api_name = supplied.title()


        if api_name.lower() not in [
            "religion",
            "religious"
        ]:

            return api_name


    # -----------------------------------------------------
    # DEFAULT
    # -----------------------------------------------------

    return "IPTV"


# =========================================================
# AUTO LOGO
# =========================================================

def find_logo(
    data,
    inherited_logo=""
):

    if not isinstance(
        data,
        dict
    ):

        return inherited_logo


    logo_fields = [

        "logo",
        "logoUrl",
        "logo_url",

        "channelLogo",
        "channel_logo",

        "image",
        "imageUrl",
        "image_url",

        "thumbnail",
        "thumbnailUrl",

        "icon",
        "iconUrl",

        "poster",
        "picture",
        "avatar"
    ]


    for field in logo_fields:

        value = data.get(
            field
        )


        if isinstance(
            value,
            str
        ):

            value = value.strip()


            if value.startswith(
                "http://"
            ) or value.startswith(
                "https://"
            ):

                return value


    return inherited_logo


# =========================================================
# NORMALIZE LOGO
# =========================================================

def normalize_logo(
    logo
):

    if not logo:
        return ""


    logo = str(
        logo
    ).strip()


    if not logo.startswith(
        (
            "http://",
            "https://"
        )
    ):

        return ""


    return logo


# =========================================================
# FETCH API
# =========================================================

def fetch_api():

    if not API_URL:

        raise Exception(
            "AYNAOTT_API_URL missing"
        )


    print(
        "Fetching API..."
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
# FIND CHANNELS
# =========================================================

def find_channels(
    data,
    channels=None,
    name="Unknown",
    logo="",
    group="Live TV"
):

    if channels is None:

        channels = []


    # =====================================================
    # DICT
    # =====================================================

    if isinstance(
        data,
        dict
    ):

        channel_name = (
            data.get("name")
            or data.get("title")
            or data.get("channelName")
            or data.get("channel_name")
            or data.get("displayName")
            or name
        )


        channel_logo = find_logo(
            data,
            logo
        )


        api_group = (
            data.get("group")
            or data.get("groupName")
            or ""
        )


        api_category = (
            data.get("category")
            or ""
        )


        api_genre = (
            data.get("genre")
            or ""
        )


        api_type = (
            data.get("type")
            or ""
        )


        channel_group = auto_category(
            channel_name,
            api_group,
            api_category,
            api_genre,
            api_type
        )


        # -------------------------------------------------
        # FIND M3U8
        # -------------------------------------------------

        for value in data.values():

            if isinstance(
                value,
                str
            ):

                urls = re.findall(
                    r'https?://[^\s"\'<>]+?\.m3u8(?:\?[^\s"\'<>]*)?',
                    value,
                    re.IGNORECASE
                )


                for stream_url in urls:

                    channels.append(
                        {
                            "name": str(
                                channel_name
                            ).strip(),

                            "url": stream_url.strip(),

                            "logo": normalize_logo(
                                channel_logo
                            ),

                            "group": channel_group
                        }
                    )


            elif isinstance(
                value,
                (dict, list)
            ):

                find_channels(
                    value,
                    channels,
                    channel_name,
                    channel_logo,
                    channel_group
                )


    # =====================================================
    # LIST
    # =====================================================

    elif isinstance(
        data,
        list
    ):

        for item in data:

            find_channels(
                item,
                channels,
                name,
                logo,
                group
            )


    return channels


# =========================================================
# CLEAN CHANNEL NAME
# =========================================================

def clean_channel_name(
    name
):

    if not name:

        return "Unknown"


    name = str(
        name
    ).strip()


    name = re.sub(
        r"\s+",
        " ",
        name
    )


    return name


# =========================================================
# REMOVE DUPLICATES
# =========================================================

def remove_duplicate(
    channels
):

    result = []

    seen_urls = set()


    for channel in channels:

        url = channel.get(
            "url",
            ""
        ).strip()


        if not url:

            continue


        url_key = url.lower()


        if url_key in seen_urls:

            continue


        seen_urls.add(
            url_key
        )


        name = clean_channel_name(
            channel.get(
                "name",
                "Unknown"
            )
        )


        logo = normalize_logo(
            channel.get(
                "logo",
                ""
            )
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
                "name": name,
                "url": url,
                "logo": logo,
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
            response.headers
            .get(
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


        # Master playlist
        if "#EXT-X-STREAM-INF" in text_upper:

            return True


        # Media playlist
        if "#EXTINF" in text_upper:

            return True


        # Other HLS playlist
        if "#EXT-X-TARGETDURATION" in text_upper:

            return True


        # Content-Type fallback
        if (
            "mpegurl" in content_type
            or "m3u8" in content_type
        ):

            return True


    except Exception:

        pass


    return False


# =========================================================
# CHECK ONE CHANNEL
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


        # -------------------------------------------------
        # HTTP STATUS
        # -------------------------------------------------

        if response.status_code != 200:

            print(
                "FAIL:",
                channel["name"],
                "| HTTP",
                response.status_code
            )

            response.close()

            return None


        # -------------------------------------------------
        # M3U8 VALIDATION
        # -------------------------------------------------

        valid = validate_m3u8_content(
            response
        )


        response.close()


        if not valid:

            print(
                "FAIL:",
                channel["name"],
                "| Invalid M3U8"
            )

            return None


        # -------------------------------------------------
        # WORKING
        # -------------------------------------------------

        print(
            "OK:",
            channel["name"],
            "|",
            channel["group"]
        )


        return channel


    except Exception:

        print(
            "FAIL:",
            channel["name"]
        )

        return None


# =========================================================
# CHECK WORKING CHANNELS
# =========================================================

def check_working_channels(
    channels
):

    working = []


    print(
        "\nChecking streams..."
    )


    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:


        futures = []


        for channel in channels:

            futures.append(
                executor.submit(
                    check_one_channel,
                    channel
                )
            )


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
# ADD ALWAYS CHANNEL
# =========================================================

def add_always_channel(
    channels
):

    always_url = ALWAYS_CHANNEL[
        "url"
    ].lower()


    # -----------------------------------------------------
    # Remove same URL if API already contains it
    # -----------------------------------------------------

    filtered = [
        channel
        for channel in channels
        if channel.get(
            "url",
            ""
        ).lower() != always_url
    ]


    # -----------------------------------------------------
    # ALWAYS ADD
    # -----------------------------------------------------

    filtered.append(
        ALWAYS_CHANNEL.copy()
    )


    return filtered


# =========================================================
# M3U ESCAPE
# =========================================================

def m3u_escape(
    value
):

    if value is None:

        return ""


    value = str(
        value
    )


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
# SORT CHANNELS
# =========================================================

def sort_channels(
    channels
):

    def sort_key(
        channel
    ):

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
# CATEGORY STATISTICS
# =========================================================

def print_category_stats(
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
                f"  {category}: "
                f"{stats[category]}"
            )


# =========================================================
# CREATE PLAYLIST
# =========================================================

def create_playlist(
    channels
):

    # Sort final channels
    channels = sort_channels(
        channels
    )


    total_channels = len(
        channels
    )


    # Current UTC time
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
            f"# #️⃣ Total Channels: "
            f"{total_channels}\n"
        )


        file.write(
            f"# 🕒 Updated: "
            f"{updated}\n"
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


        # =================================================
        # CHANNEL OUTPUT
        # =================================================

        current_category = None


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
                channel["url"]
                + "\n\n"
            )


        # =================================================
        # EMPTY
        # =================================================

        if not channels:

            file.write(
                "# No working channels found\n"
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
        "File:",
        PLAYLIST_FILE
    )

    print(
        "Total Output:",
        total_channels
    )

    print(
        "Updated:",
        updated
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "=========================================="
    )

    print(
        "AYNNA OTT AUTO PLAYLIST GENERATOR"
    )

    print(
        "=========================================="
    )

    print(
        "✓ Working Channels Only"
    )

    print(
        "✓ M3U8 Validation"
    )

    print(
        "✓ Auto Category"
    )

    print(
        "✓ Auto Logo"
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


    try:

        # =================================================
        # 1. FETCH API
        # =================================================

        data = fetch_api()


        # =================================================
        # 2. FIND CHANNELS
        # =================================================

        channels = find_channels(
            data
        )


        print(
            "\nFound:",
            len(channels)
        )


        # =================================================
        # 3. REMOVE DUPLICATES
        # =================================================

        channels = remove_duplicate(
            channels
        )


        print(
            "Unique:",
            len(channels)
        )


        # =================================================
        # 4. CHECK WORKING CHANNELS
        # =================================================

        working_channels = (
            check_working_channels(
                channels
            )
        )


        print(
            "\nWorking API Channels:",
            len(working_channels)
        )


        # =================================================
        # 5. ALWAYS ADD IPTV LINKS
        # =================================================

        final_channels = add_always_channel(
            working_channels
        )


        print(
            "Always Channel:",
            ALWAYS_CHANNEL["name"]
        )


        print(
            "Final Output:",
            len(final_channels)
        )


        # =================================================
        # 6. CATEGORY STATS
        # =================================================

        print_category_stats(
            final_channels
        )


        # =================================================
        # 7. CREATE PLAYLIST
        # =================================================

        create_playlist(
            final_channels
        )


    except Exception as error:

        print(
            "\nERROR:",
            error
        )


        # -------------------------------------------------
        # Even if API fails, ALWAYS create playlist
        # with IPTV LINKS channel.
        # -------------------------------------------------

        final_channels = [
            ALWAYS_CHANNEL.copy()
        ]


        create_playlist(
            final_channels
        )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()

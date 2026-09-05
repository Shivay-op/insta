import os
import tempfile
import time
from io import BytesIO

import requests
from yt_dlp import YoutubeDL

from config import COBALT_API, API, MAX_MEMORY_SIZE


# =========================================================
# COBALT
# =========================================================

def get_cobalt_url(url):
    try:
        print("Using Cobalt...")

        r = requests.post(
            COBALT_API,
            json={
                "url": url
            },
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=(10, 30),
        )

        print("Cobalt response:", r.text)

        r.raise_for_status()

        data = r.json()

        status = data.get("status")

        # Direct/tunnel URL
        if status in ("redirect", "tunnel"):
            return data.get("url")

        # Picker response
        if status == "picker":

            for item in data.get("picker", []):

                if item.get("type") == "video":
                    return item.get("url")

    except Exception as e:

        print(
            "Cobalt error:",
            repr(e)
        )

    return None


# =========================================================
# API FALLBACK
# =========================================================

def get_api_url(url):
    try:
        print("Using API...")

        r = requests.get(
            API,
            params={
                "url": url
            },
            timeout=(10, 60),
        )

        r.raise_for_status()

        data = r.json()

        if data.get("status"):

            return data[
                "data"
            ][
                "media"
            ][
                "download"
            ]

    except Exception as e:

        print(
            "API error:",
            repr(e)
        )

    return None


# =========================================================
# YT-DLP URL
# =========================================================

def get_ytdlp_url(url):

    try:

        print("Using yt-dlp...")

        options = {
            "quiet": True,
            "noplaylist": True,

            # Prefer MP4
            "format": (
                "best[ext=mp4]/"
                "best"
            ),

            "socket_timeout": 30,

            "retries": 5,

            "extractor_retries": 3,

            "fragment_retries": 5,

            # 10 MB HTTP chunks
            "http_chunk_size": 10 * 1024 * 1024,
        }

        with YoutubeDL(options) as ydl:

            info = ydl.extract_info(
                url,
                download=False,
            )

        if not info:
            return None

        video_url = info.get("url")

        if video_url:
            print("yt-dlp URL obtained.")

        return video_url

    except Exception as e:

        print(
            "yt-dlp error:",
            repr(e)
        )

    return None


# =========================================================
# YT-DLP DOWNLOAD COMPATIBILITY FUNCTION
# =========================================================

def download_ytdlp(url):

    """
    Compatibility function for existing link.py.

    Gets a direct video URL using yt-dlp,
    then downloads it using download_video().
    """

    print("Starting yt-dlp download...")

    video_url = get_ytdlp_url(url)

    if not video_url:

        print(
            "yt-dlp could not find video URL."
        )

        return None, None

    return download_video(
        video_url
    )


# =========================================================
# GET VIDEO URL
# =========================================================

def get_video_url(url):

    # -----------------------------------------------------
    # 1. Cobalt
    # -----------------------------------------------------

    video = get_cobalt_url(url)

    if video:

        print(
            "Cobalt URL obtained."
        )

        return video

    # -----------------------------------------------------
    # 2. API
    # -----------------------------------------------------

    print(
        "Cobalt failed."
    )

    video = get_api_url(url)

    if video:

        print(
            "API URL obtained."
        )

        return video

    # -----------------------------------------------------
    # 3. yt-dlp
    # -----------------------------------------------------

    print(
        "API failed."
    )

    video = get_ytdlp_url(url)

    if video:

        print(
            "yt-dlp URL obtained."
        )

    return video


# =========================================================
# DOWNLOAD VIDEO
# =========================================================

def download_video(
    video_url,
    max_retries=5
):

    """
    Download direct video URL.

    Small files:
        BytesIO

    Large files:
        temporary .mp4 file

    Returns:

        (video_object, temp_path)

    """

    headers = {

        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),

        "Accept": "*/*",

        "Accept-Encoding": "identity",

        "Connection": "keep-alive",
    }

    temp_path = None

    try:

        # -------------------------------------------------
        # Create temporary file
        # -------------------------------------------------

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp4",
        )

        temp_path = temp_file.name

        temp_file.close()

        downloaded = 0

        # -------------------------------------------------
        # Retry loop
        # -------------------------------------------------

        for attempt in range(
            1,
            max_retries + 1
        ):

            print(
                f"Download attempt "
                f"{attempt}/{max_retries}"
            )

            try:

                request_headers = headers.copy()

                # -----------------------------------------
                # Resume download
                # -----------------------------------------

                if downloaded > 0:

                    request_headers[
                        "Range"
                    ] = (
                        f"bytes={downloaded}-"
                    )

                    print(
                        "Resuming from:",
                        f"{downloaded / 1024 / 1024:.2f} MB"
                    )

                # -----------------------------------------
                # Request
                # -----------------------------------------

                with requests.get(
                    video_url,
                    headers=request_headers,
                    stream=True,
                    timeout=(60, 1800),
                    allow_redirects=True,
                ) as r:

                    print(
                        "HTTP status:",
                        r.status_code
                    )

                    r.raise_for_status()

                    # -------------------------------------
                    # Server ignored Range
                    # -------------------------------------

                    if (
                        downloaded > 0
                        and r.status_code == 200
                    ):

                        print(
                            "Server ignored Range."
                        )

                        print(
                            "Restarting download..."
                        )

                        downloaded = 0

                        with open(
                            temp_path,
                            "wb",
                        ):
                            pass

                    # -------------------------------------
                    # File mode
                    # -------------------------------------

                    if downloaded > 0:
                        mode = "ab"
                    else:
                        mode = "wb"

                    # -------------------------------------
                    # Write chunks
                    # -------------------------------------

                    with open(
                        temp_path,
                        mode,
                    ) as f:

                        for chunk in r.iter_content(
                            chunk_size=1024 * 1024
                        ):

                            if not chunk:
                                continue

                            f.write(chunk)

                            downloaded += len(
                                chunk
                            )

                            print(
                                "\rDownloaded: "
                                f"{downloaded / 1024 / 1024:.2f} MB",
                                end="",
                                flush=True,
                            )

                print()

                print(
                    "Download completed."
                )

                # -----------------------------------------
                # Verify file
                # -----------------------------------------

                if not os.path.exists(
                    temp_path
                ):

                    raise RuntimeError(
                        "Downloaded file "
                        "does not exist."
                    )

                final_size = os.path.getsize(
                    temp_path
                )

                print(
                    "Final file size:",
                    f"{final_size / 1024 / 1024:.2f} MB"
                )

                if final_size <= 0:

                    raise RuntimeError(
                        "Downloaded file is empty."
                    )

                # -----------------------------------------
                # Small file -> RAM
                # -----------------------------------------
                print("Video stored on disk.")
                return temp_path, temp_path

       
                # -----------------------------------------
                # Large file -> disk
                # -----------------------------------------
            # -------------------------------------------------
            # Connection timeout / disconnect
            # -------------------------------------------------

            except (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
            ) as e:

                print()

                print(
                    "Connection error:",
                    repr(e)
                )

                # -----------------------------------------
                # Get actual downloaded size
                # -----------------------------------------

                if os.path.exists(
                    temp_path
                ):

                    downloaded = os.path.getsize(
                        temp_path
                    )

                print(
                    "Downloaded so far:",
                    f"{downloaded / 1024 / 1024:.2f} MB"
                )

                # -----------------------------------------
                # Last attempt
                # -----------------------------------------

                if attempt >= max_retries:

                    raise

                wait = min(
                    2 ** (attempt - 1),
                    30,
                )

                print(
                    f"Retrying in {wait} seconds..."
                )

                time.sleep(
                    wait
                )

        raise RuntimeError(
            "Maximum download retries exceeded."
        )

    except Exception as e:

        print(
            "Download error:",
            repr(e)
        )

        # -------------------------------------------------
        # Cleanup
        # -------------------------------------------------

        if temp_path:

            try:

                if os.path.exists(
                    temp_path
                ):

                    os.remove(
                        temp_path
                    )

            except Exception as cleanup_error:

                print(
                    "Cleanup error:",
                    repr(cleanup_error)
                )

        return (
            None,
            None
        )


# =========================================================
# COMPLETE PROCESS
# =========================================================

def process_video(url):

    """
    Complete downloader:

        Facebook/Instagram URL
                ↓
             Cobalt
                ↓
              API
                ↓
             yt-dlp
                ↓
             Download
    """

    print(
        "================================"
    )

    print(
        "Getting video URL..."
    )

    print(
        "================================"
    )

    video_url = get_video_url(
        url
    )

    if not video_url:

        print(
            "Could not obtain video URL."
        )

        return (
            None,
            None
        )

    print(
        "Video URL obtained."
    )

    # -----------------------------------------------------
    # Download
    # -----------------------------------------------------

    video, temp_path = download_video(
        video_url
    )

    if video is None:

        print(
            "Video download failed."
        )

        return (
            None,
            None
        )

    print(
        "Video ready."
    )

    return (
        video,
        temp_path
    )


# =========================================================
# DELETE TEMP FILE
# =========================================================

def delete_temp(path):

    if not path:
        return

    try:

        if os.path.exists(path):

            os.remove(path)

            print(
                "Temporary file deleted."
            )

    except Exception as e:

        print(
            "Delete error:",
            repr(e)
        )

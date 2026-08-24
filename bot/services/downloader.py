import os
import tempfile
import requests

from io import BytesIO
from yt_dlp import YoutubeDL

from config import COBALT_API, API, MAX_MEMORY_SIZE


def get_cobalt_url(url):

    try:
        r = requests.post(
            COBALT_API,
            json={
                "url": url
            },
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=(3, 15)
        )

        print("Cobalt response:", r.text)

        r.raise_for_status()

        data = r.json()

        if data.get("status") in [
            "tunnel",
            "redirect"
        ]:
            return data.get("url")

        if data.get("status") == "picker":
            for item in data.get("picker", []):
                if item.get("type") == "video":
                    return item.get("url")

    except Exception as e:
        print("Cobalt error:", e)

    return None



def get_api_url(url):

    try:
        r = requests.get(
            API,
            params={
                "url": url
            },
            timeout=(10, 60)
        )

        r.raise_for_status()

        data = r.json()

        if data.get("status"):
            return data["data"]["media"]["download"]

    except Exception as e:
        print("API error:", e)

    return None



def get_ytdlp_url(url):

    try:

        options = {
            "quiet": True,
            "noplaylist": True,
            "format": "best[ext=mp4]/best",
            "socket_timeout": 15,
            "retries": 2,
            "extractor_retries": 1,
            "fragment_retries": 2
        }


        with YoutubeDL(options) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )


        return info.get("url")


    except Exception as e:
        print("yt-dlp error:", e)

    return None



def get_video_url(url):

    # 1. Self hosted Cobalt
    video = get_cobalt_url(url)

    if video:
        return video


    # 2. Your existing API
    video = get_api_url(url)

    if video:
        return video


    # 3. yt-dlp fallback
    video = get_ytdlp_url(url)

    return video



def download_video(video_url):

    try:
        headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Encoding": "identity",
    "Connection": "keep-alive"
}

        r = requests.get(
            video_url,
            headers=headers,
            stream=True,
            timeout=(30, 600)
        )

        r.raise_for_status()


        memory = BytesIO()

        temp = None

        size = 0


        for chunk in r.iter_content(
            chunk_size=1024 * 1024
        ):

            if not chunk:
                continue


            size += len(chunk)


            # Store small files in memory
            if temp is None and size <= MAX_MEMORY_SIZE:

                memory.write(chunk)


            else:

                # Move to disk for large files
                if temp is None:

                    temp = tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".mp4"
                    )

                    memory.seek(0)

                    temp.write(
                        memory.read()
                    )

                    memory.close()


                temp.write(chunk)



        # Small file
        if temp is None:

            memory.seek(0)

            memory.name = "video.mp4"

            return memory, None



        # Large file
        temp.close()

        return temp.name, temp.name



    except Exception as e:

        print("Download error:", e)

        return None, None



def delete_temp(path):

    if path and os.path.exists(path):

        try:
            os.remove(path)

        except Exception as e:
            print("Delete error:", e)

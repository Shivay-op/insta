import os
import telebot
from concurrent.futures import (
    ThreadPoolExecutor,
    TimeoutError as FuturesTimeoutError
)

from config import BOT_USERNAME, MAX_WORKERS, CHANNEL, SUPPORT
from bot.keyboards import video_buttons
from bot.services.downloader import get_video_url, download_video, delete_temp
from bot.handlers.join import is_user_joined


executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

URL_FETCH_TIMEOUT = 45   # seconds to resolve a direct video URL
DOWNLOAD_TIMEOUT = 120   # seconds to download the video itself


def _run_with_timeout(fn, args, timeout):
    """Run fn(*args) with a hard wall-clock timeout.

    On timeout we stop waiting and report failure immediately instead of
    leaving the user staring at "Processing..." forever; the underlying
    call (network I/O we can't interrupt) is left to finish on its own.
    """
    worker = ThreadPoolExecutor(max_workers=1)
    future = worker.submit(fn, *args)
    try:
        return future.result(timeout=timeout)
    finally:
        worker.shutdown(wait=False)


SUPPORTED_DOMAINS = [
    "instagram.com",
    "tiktok.com",
    "youtube.com",
    "youtu.be",
    "twitter.com",
    "x.com",
    "reddit.com",
    "facebook.com",
    "fb.watch",
    "vimeo.com",
    "pinterest.com",
    "snapchat.com",
    "twitch.tv",
    "soundcloud.com",
    "dailymotion.com",
    "bilibili.com",
    "streamable.com"
]


def register(bot):

    def process_reel(message, processing):
        video_data = None
        try:
            clean_url = message.text.split("?")[0]

            # 1. Get video URL
            try:
                url_result = _run_with_timeout(
                    get_video_url, (clean_url,), URL_FETCH_TIMEOUT
                )
            except FuturesTimeoutError:
                bot.edit_message_text(
                    "❌ Timed out fetching this video. Please try again later.",
                    message.chat.id,
                    processing.message_id
                )
                return

            video_url = url_result[0] if isinstance(url_result, tuple) else url_result

            if not video_url:
                bot.edit_message_text(
                    "❌ Could not fetch video. Make sure the account is public.",
                    message.chat.id,
                    processing.message_id
                )
                return

            # 2. Download video
            try:
                download_result = _run_with_timeout(
                    download_video, (video_url,), DOWNLOAD_TIMEOUT
                )
            except FuturesTimeoutError:
                bot.edit_message_text(
                    "❌ Download took too long. Please try again later.",
                    message.chat.id,
                    processing.message_id
                )
                return

            video_data = download_result[0] if isinstance(download_result, tuple) else download_result

            if not video_data:
                bot.edit_message_text(
                    "❌ Failed to download Reel. Please try again later.",
                    message.chat.id,
                    processing.message_id
                )
                return

            # 3. Send video (Handles both BytesIO memory streams and file paths)
            if hasattr(video_data, "read"):  # It's a BytesIO / memory stream
                video_data.seek(0)
                # Telegram requires a filename attribute to recognize it as an MP4
                if not hasattr(video_data, "name") or not video_data.name:
                    video_data.name = "reel.mp4"

                bot.send_video(
                    message.chat.id,
                    video_data,
                    caption=f"🚀 Downloaded via {BOT_USERNAME}",
                    reply_to_message_id=message.message_id,
                    reply_markup=video_buttons()
                )

            elif isinstance(video_data, str):  # It's a file path string
                with open(video_data, "rb") as video:
                    bot.send_video(
                        message.chat.id,
                        video,
                        caption=f"🚀 Downloaded via {BOT_USERNAME}",
                        reply_to_message_id=message.message_id,
                        reply_markup=video_buttons()
                    )

            bot.delete_message(message.chat.id, processing.message_id)

        except Exception as e:
            print(f"Error processing reel: {e}")
            try:
                bot.edit_message_text(
                    "❌ Failed to download Reel. Please try again later.",
                    message.chat.id,
                    processing.message_id
                )
            except Exception:
                pass

        finally:
            # 4. Clean up safely
            try:
                if isinstance(video_data, str) and os.path.exists(video_data):
                    delete_temp(video_data)
                elif hasattr(video_data, "close"):
                    video_data.close()
            except Exception as e:
                print(f"Cleanup error: {e}")

    @bot.message_handler(
        func=lambda m: (
            m.text and
            any(
                domain in m.text.lower()
                for domain in SUPPORTED_DOMAINS
            )
        )
    )
    def handle_link(message):

        if not is_user_joined(bot, message.from_user.id):

            markup = telebot.types.InlineKeyboardMarkup()

            markup.add(
                telebot.types.InlineKeyboardButton(
                    "📢 Join Channel",
                    url=CHANNEL
                )
            )

            markup.add(
                telebot.types.InlineKeyboardButton(
                    "💬 Join Support",
                    url=SUPPORT
                )
            )

            markup.add(
                telebot.types.InlineKeyboardButton(
                    "✅ I Joined",
                    callback_data="check_join"
                )
            )

            bot.reply_to(
                message,
                "⚠️ Please join our channel and support group first.\n\n"
                "After joining, click the button below to verify.",
                reply_markup=markup
            )

            return


        processing = bot.reply_to(
            message,
            "⏳ Processing your video..."
        )

        executor.submit(
            process_reel,
            message,
            processing
        )

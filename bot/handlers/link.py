import os
import telebot

from concurrent.futures import ThreadPoolExecutor

from config import (
    BOT_USERNAME,
    MAX_WORKERS,
    CHANNEL,
    SUPPORT,
)

from bot.keyboards import video_buttons

from bot.services.downloader import (
    get_video_url,
    download_video,
    delete_temp,
)

from bot.handlers.join import is_user_joined


executor = ThreadPoolExecutor(
    max_workers=MAX_WORKERS
)


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
    "streamable.com",
]


def register(bot):

    def process_reel(message, processing):

        video_data = None
        temp_path = None

        try:

            # =================================================
            # Clean URL
            # =================================================

            clean_url = (
                message.text
                .strip()
                .split("?")[0]
            )

            print(
                "Processing URL:",
                clean_url
            )

            # =================================================
            # STEP 1 - GET VIDEO URL
            # =================================================

            print(
                "Getting video URL..."
            )

            video_url = get_video_url(
                clean_url
            )

            if isinstance(
                video_url,
                tuple
            ):
                video_url = video_url[0]

            if not video_url:

                bot.edit_message_text(
                    "❌ Could not fetch this video.\n"
                    "Make sure the video/account is public.",
                    message.chat.id,
                    processing.message_id,
                )

                return

            print(
                "Video URL received."
            )

            # =================================================
            # STEP 2 - DOWNLOAD
            # =================================================

            print(
                "Starting download..."
            )

            download_result = download_video(
                video_url
            )

            if not download_result:

                bot.edit_message_text(
                    "❌ Failed to download the video.\n"
                    "Please try again later.",
                    message.chat.id,
                    processing.message_id,
                )

                return

            # =================================================
            # Extract result
            # =================================================

            if isinstance(
                download_result,
                tuple
            ):

                video_data = download_result[0]

                temp_path = download_result[1]

            else:

                video_data = download_result

            if not video_data:

                bot.edit_message_text(
                    "❌ Download failed.",
                    message.chat.id,
                    processing.message_id,
                )

                return

            print(
                "Video downloaded successfully."
            )

            # =================================================
            # STEP 3 - SEND VIDEO
            # =================================================

            print(
                "Uploading video to Telegram..."
            )

            # -------------------------------------------------
            # BytesIO
            # -------------------------------------------------

            if hasattr(
                video_data,
                "read"
            ):

                video_data.seek(0)

                try:
                    video_data.name
                except AttributeError:
                    video_data.name = (
                        "reel.mp4"
                    )

                bot.send_video(
                    chat_id=message.chat.id,

                    video=video_data,

                    caption=(
                        f"🚀 Downloaded via "
                        f"{BOT_USERNAME}"
                    ),

                    reply_to_message_id=(
                        message.message_id
                    ),

                    reply_markup=video_buttons(),

                    supports_streaming=True,
                    timeout=1800,
                )

            # -------------------------------------------------
            # File path
            # -------------------------------------------------

            elif isinstance(
                video_data,
                str
            ):

                if not os.path.exists(
                    video_data
                ):

                    raise FileNotFoundError(
                        video_data
                    )

                with open(
                    video_data,
                    "rb"
                ) as video:

                    bot.send_video(
                        chat_id=message.chat.id,

                        video=video,

                        caption=(
                            f"🚀 Downloaded via "
                            f"{BOT_USERNAME}"
                        ),

                        reply_to_message_id=(
                            message.message_id
                        ),

                        reply_markup=video_buttons(),

                        supports_streaming=True,
                        timeout=1800,
                    )

            else:

                raise TypeError(
                    "Unknown video type: "
                    f"{type(video_data)}"
                )

            print(
                "Telegram upload completed."
            )

            # =================================================
            # STEP 4 - DELETE PROCESSING MESSAGE
            # =================================================

            try:

                bot.delete_message(
                    message.chat.id,
                    processing.message_id
                )

            except Exception as e:

                print(
                    "Could not delete processing message:",
                    repr(e)
                )

        except Exception as e:

            print(
                "Error processing reel:",
                repr(e)
            )

            try:

                bot.edit_message_text(
                    "❌ Failed to download/send the video.\n"
                    "Please try again later.",
                    message.chat.id,
                    processing.message_id,
                )

            except Exception as edit_error:

                print(
                    "Error editing message:",
                    repr(edit_error)
                )

        finally:

            # =================================================
            # CLEANUP
            # =================================================

            try:

                if temp_path:

                    if os.path.exists(
                        temp_path
                    ):

                        delete_temp(
                            temp_path
                        )

                elif isinstance(
                    video_data,
                    str
                ):

                    if os.path.exists(
                        video_data
                    ):

                        delete_temp(
                            video_data
                        )

                elif hasattr(
                    video_data,
                    "close"
                ):

                    video_data.close()

            except Exception as e:

                print(
                    "Cleanup error:",
                    repr(e)
                )

    # =========================================================
    # LINK HANDLER
    # =========================================================

    @bot.message_handler(
        func=lambda m: (
            m.text
            and any(
                domain in m.text.lower()
                for domain in SUPPORTED_DOMAINS
            )
        )
    )
    def handle_link(message):

        # =====================================================
        # JOIN CHECK
        # =====================================================

        if not is_user_joined(
            bot,
            message.from_user.id
        ):

            markup = (
                telebot.types
                .InlineKeyboardMarkup()
            )

            markup.add(
                telebot.types
                .InlineKeyboardButton(
                    "📢 Join Channel",
                    url=CHANNEL,
                )
            )

            markup.add(
                telebot.types
                .InlineKeyboardButton(
                    "💬 Join Support",
                    url=SUPPORT,
                )
            )

            markup.add(
                telebot.types
                .InlineKeyboardButton(
                    "✅ I Joined",
                    callback_data="check_join",
                )
            )

            bot.reply_to(
                message,

                "⚠️ Please join our channel "
                "and support group first.\n\n"
                "After joining, click the "
                "button below to verify.",

                reply_markup=markup,
            )

            return

        # =====================================================
        # PROCESSING MESSAGE
        # =====================================================

        processing = bot.reply_to(
            message,
            "⏳ Processing your video..."
        )

        # =====================================================
        # BACKGROUND PROCESS
        # =====================================================

        executor.submit(
            process_reel,
            message,
            processing,
        )

from config import BOT_USERNAME, CHANNEL_ID
from bot.keyboards import video_buttons
from bot.services.database import add_user


def register(bot):

    @bot.message_handler(commands=["start"])
    def start(message):

        total_users = add_user(message.from_user)
        user = message.from_user
        name = user.first_name or "Unknown"

        username = (
            f"@{user.username}" if user.username else "No Username"
        )

        user_link = f'<a href="tg://user?id={user.id}">{name}</a>'

        notify = f"""
🆕 New User Notification 🆕

👩‍💻 Name : {name}

👉 Username : {username}

🔗 User Link : {user_link}

🆔 User ID : {user.id}

📊 Total Users : {total_users}
"""

        try:
            bot.send_message(CHANNEL_ID, notify, parse_mode="HTML")
        except Exception as e:
            print("Channel notification error:", e)

        welcome = f"""
👋 Welcome to Instagram Reel Downloader Bot!

📥 Send any public Instagram Reel link.

⚡ Features:
• Fast download
• High quality video
• Multiple users supported
• Auto cleanup

🚀 Powered by {BOT_USERNAME}
"""

        bot.reply_to(message, welcome, reply_markup=video_buttons())

from config import CHANNEL, SUPPORT


def extract_chat_username(url):

    return (
        url
        .replace("https://t.me/", "")
        .replace("@", "")
        .strip()
    )


def is_user_joined(bot, user_id):

    required_channels = [
        extract_chat_username(CHANNEL),
        extract_chat_username(SUPPORT)
    ]

    for chat in required_channels:

        try:

            member = bot.get_chat_member(
                chat_id=f"@{chat}",
                user_id=user_id
            )

            if member.status in ["left", "kicked"]:
                return False

        except Exception as e:
            print("Join check error:", e)
            return False

    return True


def register(bot):

    @bot.callback_query_handler(
        func=lambda call: call.data == "check_join"
    )
    def check_join(call):

        if is_user_joined(bot, call.from_user.id):

            bot.answer_callback_query(
                call.id,
                "✅ Verified!"
            )

            bot.edit_message_text(
                "✅ Verification successful.\n\n"
                "Now send your video link.",
                call.message.chat.id,
                call.message.message_id
            )

        else:

            bot.answer_callback_query(
                call.id,
                "❌ Please join first.",
                show_alert=True
            )

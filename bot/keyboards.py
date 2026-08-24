from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL, SUPPORT


def video_buttons():

    markup = InlineKeyboardMarkup(row_width=2)

    markup.add(
        InlineKeyboardButton(
            "📢 Channel",
            url=CHANNEL
        ),
        InlineKeyboardButton(
            "💬 Support",
            url=SUPPORT
        )
    )

    return markup

import telebot

from config import BOT_TOKEN
from bot.handlers import setup_handlers


bot = telebot.TeleBot(BOT_TOKEN)

setup_handlers(bot)

print("Bot Started...")

bot.infinity_polling(skip_pending=True)

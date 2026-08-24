import os

BOT_TOKEN = ""

API = "https://tele-social.vercel.app/down"

COBALT_API = "http://127.0.0.1:9000/"

BOT_USERNAME = "@downloader_hubbot"

CHANNEL_ID = -1002446116389

ADMIN_ID = 6744775967


CHANNEL = "https://t.me/itsteachteam"
SUPPORT = "https://t.me/itsteachteamsupport"

MAX_MEMORY_SIZE = 50 * 1024 * 1024

MAX_WORKERS = 5

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

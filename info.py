import os

# ---------------- Core Telegram / Bot Config ----------------
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# ---------------- Database ----------------
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "SpideyShareBot")

# ---------------- Owner / Admins ----------------
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
ADMINS = [OWNER_ID] + [int(x) for x in os.environ.get("ADMINS", "").split() if x.isdigit()]

# ---------------- Branding ----------------
BOT_NAME = os.environ.get("BOT_NAME", "SpideyShareBot")
DEVELOPER = "@Spidey2189"
SUPPORT_CHANNELS = ["@spideyoffcail", "@mvxyoffcail"]

# Logs channel where new submissions / admin actions get posted (optional)
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))

# ---------------- Welcome / Media ----------------
STICKER_ID = "CAACAgIAAxkBAAEQZtFpgEdROhGouBVFD3e0K-YjmVHwsgACtCMAAphLKUjeub7NKlvk2TgE"
PICS_URL = ["https://api.aniwallpaper.workers.dev/random?type=girl"]

# ---------------- Limits ----------------
FREE_USER_CHANNEL_LIMIT = 3
PAGE_SIZE = 5

# ---------------- Default categories (seeded on first run) ----------------
DEFAULT_CATEGORIES = [
    "Movies", "Web Series", "Anime", "Music", "Educational",
    "Gaming", "News", "Technology", "Premium Channels", "Bots",
]

import os

# ---------------- Core Telegram / Bot Config ----------------
API_ID = 36282056
API_HASH = "3a948acece533f362b4c90b2b3c14b60"
BOT_TOKEN = "8530838101:AAFD9MQdmsqST4LConoHCvl4vBXCRLVuipo"

# ---------------- Database ----------------
MONGO_URI = "mongodb+srv://cloudnestoffcail_db_user:Venura8907@cluster0.hjqkg75.mongodb.net/?appName=Cluster0"
DB_NAME = "SpideyShareBot"

# ---------------- Owner / Admins ----------------
OWNER_ID = "8498741978"
ADMINS = [8498741978]

# ---------------- Branding ----------------
BOT_NAME = "SpideyShareBot"
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

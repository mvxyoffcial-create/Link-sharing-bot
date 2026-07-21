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
ADMIN_ID = 8498741978  # For compatibility with new features
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
FREE_USER_CHANNEL_LIMIT = 3  # Max listings for free users
FREE_USER_DAILY_VERIFICATIONS = 2  # Max verifications per day for free users
FREE_PROPERTY_DURATION_HOURS = 24  # Auto-removal after 24 hours for free listings
PAGE_SIZE = 5

# ---------------- Verification API ----------------
VERIFICATION_API = "https://userlinks.in/st?api=920693e8f5b3e7289bd203327543123631080f07&url="

# ---------------- Premium Settings ----------------
PREMIUM_PROPERTY_DURATION_DAYS = 30  # Premium listings last 30 days

# ---------------- Default categories (seeded on first run) ----------------
DEFAULT_CATEGORIES = [
    "Movies", "Web Series", "Anime", "Music", "Educational",
    "Gaming", "News", "Technology", "Premium Channels", "Bots",
]

# ---------------- Bot Messages (Optional overrides) ----------------
# These are defined in script.py, but you can override them here if needed

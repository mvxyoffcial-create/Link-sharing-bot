# SpideyShareBot — Channel, Group & Bot Sharing Bot

Developer: **@Spidey2189**

A Telegram bot (Pyrogram + MongoDB) where users can list and discover channels, groups and bots
across categories, with an ownership-verification system and a premium tier.

## Features
- Animated welcome + dynamic welcome image
- Main menu: Browse Categories, Add Listing, Profile, Premium Info, Search, Top Listings, Help, About
- Add-listing conversation flow (name → link → category → description) with automatic
  ownership verification (bot checks if you're an admin/creator of the chat you submit)
- Category browsing with pagination and Join buttons
- Free users: 3 listings max, must be verified to join others' listings
- Premium users: unlimited listings, instant join access, no verification wait
- `/info` profile command with stats and profile photo
- Admin panel: `/stats`, `/broadcast`, `/add_category`, `/remove_category`,
  `/add_premium`, `/remove_premium`, `/verify_channel`, `/delete_channel`, `/admin_list`
- Keyword auto-filter search + `/search` via inline button
- Top Listings leaderboard by join count

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Copy `.env.sample` to `.env` (or export the vars directly) and fill in:
   - `API_ID`, `API_HASH` — from https://my.telegram.org
   - `BOT_TOKEN` — from @BotFather
   - `MONGO_URI` — MongoDB connection string
   - `OWNER_ID`, `ADMINS` — space-separated Telegram user IDs
   - `LOG_CHANNEL` — optional channel ID for submission/action logs
3. Run:
   ```
   python3 main.py
   ```

## Deployment
Works out of the box on Heroku, Railway, or any VPS — see `Procfile`.

## Project Structure
```
sharebot/
├── main.py              # entry point
├── info.py               # config / env vars
├── script.py              # text templates
├── utils.py                # helpers + in-memory conversation state
├── database/
│   └── db.py                # MongoDB (motor) access layer
└── plugins/
    ├── start.py              # /start, /help, /about, main menu
    ├── profile.py            # /info profile
    ├── channels.py           # add/browse/join/search listings
    ├── callbacks.py          # menu navigation callbacks
    └── admin.py              # admin commands
```

## Notes
- Conversation state (the add-listing wizard) is kept in memory — fine for a single worker
  process. For multi-instance deployments, swap `utils.temp` for a shared store (e.g. Redis).
- Support channels referenced in the bot text: `@spideyoffcail`, `@mvxyoffcail` — update these
  in `info.py` (`SUPPORT_CHANNELS`) if that's not your setup.

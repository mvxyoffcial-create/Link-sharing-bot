import asyncio
import logging

from pyrogram import Client

from info import API_ID, API_HASH, BOT_TOKEN
from database.db import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

app = Client(
    "SpideyShareBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins"),
    workers=200,
)


async def boot():
    await db.ensure_default_categories()
    me = await app.get_me()
    logging.info(f"{me.first_name} (@{me.username}) is up and running — dev @Spidey2189")


if __name__ == "__main__":
    async def main():
        await app.start()
        await boot()
        await asyncio.Event().wait()  # run forever

    try:
        asyncio.get_event_loop().run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        pass

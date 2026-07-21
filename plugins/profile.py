import datetime

from pyrogram import Client, filters
from pyrogram.types import Message

from database.db import db


async def build_profile_text(client: Client, user) -> str:
    data = await db.get_user(user.id)
    channel_count = await db.user_channel_count(user.id)

    is_premium = await db.is_premium(user.id)
    premium_until = data.get("premium_until") if data else None
    premium_str = premium_until.strftime("%d-%m-%Y %I:%M %p") if premium_until else "N/A"

    dc_id = getattr(user, "dc_id", "N/A")

    return (
        "👤 <b>Your Profile</b>\n\n"
        f"➲ First Name: {user.first_name or ''}\n"
        f"➲ Last Name: {user.last_name or 'None'}\n"
        f"➲ Telegram ID: <code>{user.id}</code>\n"
        f"➲ Data Centre: {dc_id}\n"
        f"➲ Username: @{user.username or 'None'}\n"
        f"➲ User Link: <a href='tg://user?id={user.id}'>Click Here</a>\n"
        "─────────────\n"
        "📊 <b>Stats:</b>\n"
        f"➲ Listings Added: {channel_count}\n"
        f"➲ Premium Status: {'Yes ✅' if is_premium else 'No ❌'}\n"
        f"➲ Premium Until: {premium_str}"
    )


@Client.on_message(filters.command("info") & filters.private)
async def info_cmd(client: Client, message: Message):
    text = await build_profile_text(client, message.from_user)
    try:
        photos = await client.get_chat_photos(message.from_user.id, limit=1)
        photo = None
        async for p in photos:
            photo = p
            break
        if photo:
            await message.reply_photo(photo.file_id, caption=text)
            return
    except Exception:
        pass
    await message.reply_text(text)

import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from database.db import db
from info import FREE_USER_CHANNEL_LIMIT, ADMIN_ID, FREE_PROPERTY_DURATION_HOURS


async def build_profile_text(client: Client, user) -> str:
    data = await db.get_user(user.id)
    channel_count = await db.user_channel_count(user.id)

    is_premium = await db.is_premium(user.id)
    premium_until = data.get("premium_until") if data else None
    
    max_listings = "Unlimited" if is_premium else FREE_USER_CHANNEL_LIMIT
    
    premium_str = "Not Premium ❌"
    if is_premium and premium_until:
        if isinstance(premium_until, datetime.datetime):
            days_left = (premium_until - datetime.datetime.utcnow()).days
            premium_str = f"Active ✅ ({days_left} days left)"
        else:
            premium_str = "Active ✅"
    elif is_premium:
        premium_str = "Active ✅"

    listings = await db.channels_by_owner(user.id)
    approved_listings = sum(1 for l in listings if l.get('approved', False))
    pending_listings = sum(1 for l in listings if not l.get('approved', False))
    expired_listings = 0
    
    for l in listings:
        if l.get('approved', False) and not l.get('is_premium', False):
            expires_at = l.get('expires_at')
            if expires_at:
                if isinstance(expires_at, str):
                    expires_at = datetime.datetime.fromisoformat(expires_at)
                if datetime.datetime.now() > expires_at:
                    expired_listings += 1

    dc_id = getattr(user, "dc_id", "N/A")
    joined_date = data.get("joined_date") if data else None
    if joined_date:
        if isinstance(joined_date, datetime.datetime):
            joined_date = joined_date.strftime("%Y-%m-%d")
        else:
            joined_date = "N/A"
    else:
        joined_date = "N/A"

    return (
        "👤 <b>Your Profile</b>\n\n"
        f"➲ First Name: {user.first_name or ''}\n"
        f"➲ Telegram ID: <code>{user.id}</code>\n"
        f"➲ Username: @{user.username or 'None'}\n"
        f"➲ Joined Date: {joined_date}\n"
        "─────────────\n"
        "📊 <b>Stats:</b>\n"
        f"➲ Listings Added: {channel_count}/{max_listings}\n"
        f"➲ Approved: {approved_listings}\n"
        f"➲ Pending: {pending_listings}\n"
        f"➲ Expired: {expired_listings}\n"
        "─────────────\n"
        "💎 <b>Premium:</b>\n"
        f"➲ Status: {premium_str}\n"
        f"➲ Free limit: {FREE_USER_CHANNEL_LIMIT} listing\n"
        f"➲ Free expiry: {FREE_PROPERTY_DURATION_HOURS} hours\n"
        f"➲ Premium: Unlimited, no expiry\n"
    )


@Client.on_message(filters.command("profile") & filters.private)
async def profile_cmd(client: Client, message: Message):
    text = await build_profile_text(client, message.from_user)
    
    try:
        photos = await client.get_chat_photos(message.from_user.id, limit=1)
        photo = None
        async for p in photos:
            photo = p
            break
        if photo:
            await message.reply_photo(
                photo.file_id, 
                caption=text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📊 My Listings", callback_data="my_listings")],
                    [InlineKeyboardButton("💎 Premium Info", callback_data="premium_info")],
                    [InlineKeyboardButton("📋 Main Menu", callback_data="main_menu")]
                ])
            )
            return
    except Exception:
        pass
    
    await message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 My Listings", callback_data="my_listings")],
            [InlineKeyboardButton("💎 Premium Info", callback_data="premium_info")],
            [InlineKeyboardButton("📋 Main Menu", callback_data="main_menu")]
        ])
    )


@Client.on_message(filters.command("info") & filters.private)
async def info_cmd(client: Client, message: Message):
    await profile_cmd(client, message)

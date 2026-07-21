import asyncio

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

from database.db import db
from info import STICKER_ID, PICS_URL, DEVELOPER, SUPPORT_CHANNELS, ADMIN_ID, FREE_USER_CHANNEL_LIMIT, FREE_PROPERTY_DURATION_HOURS
from script import script
from utils import get_welcome_image


def main_menu_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📂 Browse Categories", callback_data="browse_categories")],
        [InlineKeyboardButton("➕ Add Your Channel/Group/Bot", callback_data="add_listing")],
        [InlineKeyboardButton("👤 My Profile", callback_data="profile"),
         InlineKeyboardButton("💎 Premium Info", callback_data="premium_info")],
        [InlineKeyboardButton("🔎 Search", callback_data="search_prompt"),
         InlineKeyboardButton("🏆 Top Listings", callback_data="top_listings")],
        [InlineKeyboardButton("❓ Help", callback_data="help_menu"),
         InlineKeyboardButton("ℹ️ About", callback_data="about_menu")],
    ])


@Client.on_message(filters.command("start") & filters.private)
async def start(client: Client, message: Message):
    user = message.from_user
    await db.add_user(user.id, user.first_name or "", user.last_name or "", user.username or "")

    try:
        sticker_msg = await message.reply_sticker(STICKER_ID)
        await asyncio.sleep(2)
        await sticker_msg.delete()
    except Exception:
        pass

    try:
        await message.reply_photo(
            photo=get_welcome_image(PICS_URL),
            caption=script.WELCOME_TXT.format(first_name=user.first_name or "there"),
            reply_markup=main_menu_markup(),
        )
    except Exception:
        await message.reply_text(
            script.WELCOME_TXT.format(first_name=user.first_name or "there"),
            reply_markup=main_menu_markup(),
            disable_web_page_preview=True,
        )


@Client.on_message(filters.command("help") & filters.private)
async def help_cmd(client: Client, message: Message):
    await message.reply_text(
        script.HELP_TXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")],
            [InlineKeyboardButton("💎 Premium Info", callback_data="premium_info")]
        ]),
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command("about") & filters.private)
async def about_cmd(client: Client, message: Message):
    await message.reply_text(
        script.ABOUT_TXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]),
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command("profile") & filters.private)
async def profile_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    
    if not user:
        await message.reply_text("❌ User not found. Please use /start first.")
        return
    
    is_premium = await db.is_premium(user_id)
    listings = await db.user_channel_count(user_id)
    
    user_type = "⭐ Premium" if is_premium else "📊 Free"
    max_listings = "Unlimited" if is_premium else FREE_USER_CHANNEL_LIMIT
    
    premium_status = ""
    if is_premium:
        premium_until = user.get('premium_until')
        if premium_until:
            if isinstance(premium_until, datetime):
                days_left = (premium_until - datetime.utcnow()).days
                premium_status = f"✅ Premium active ({days_left} days left)"
            else:
                premium_status = "✅ Premium active"
    else:
        premium_status = f"🔒 Free user - {FREE_USER_CHANNEL_LIMIT} listing only, expires in {FREE_PROPERTY_DURATION_HOURS} hours"
    
    joined_date = user.get('joined_date', datetime.utcnow())
    if isinstance(joined_date, datetime):
        joined_date = joined_date.strftime("%Y-%m-%d")
    
    await message.reply_text(
        script.PROFILE_TXT.format(
            user_id=user_id,
            name=message.from_user.first_name or "User",
            user_type=user_type,
            listings=listings,
            max_listings=max_listings,
            joined_date=joined_date,
            premium_status=premium_status
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 My Listings", callback_data="my_listings")],
            [InlineKeyboardButton("💎 Premium Info", callback_data="premium_info")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ])
    )


@Client.on_message(filters.command("premium") & filters.private)
async def premium_cmd(client: Client, message: Message):
    await message.reply_text(
        script.PREMIUM_TXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Subscribe Now", callback_data="subscribe_premium")],
            [InlineKeyboardButton("📞 Contact Admin", url=f"tg://user?id={ADMIN_ID}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]),
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command("search") & filters.private)
async def search_cmd(client: Client, message: Message):
    await message.reply_text(
        "🔎 **Search Listings**\n\n"
        "Send me a keyword to search for channels, groups, or bots.\n\n"
        "Examples:\n"
        "• `movies` - Find movie channels\n"
        "• `anime` - Find anime groups\n"
        "• `music` - Find music bots\n\n"
        "Send your keyword now:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ])
    )

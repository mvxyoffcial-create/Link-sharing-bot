import asyncio

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from database.db import db
from info import STICKER_ID, PICS_URL, DEVELOPER, SUPPORT_CHANNELS
from script import script
from utils import get_welcome_image


def main_menu_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📂 Browse Categories", callback_data="browse_categories")],
        [InlineKeyboardButton("➕ Add Your Channel/Group/Bot", callback_data="add_listing")],
        [InlineKeyboardButton("👤 My Profile", callback_data="my_profile"),
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
        # Fall back to text-only welcome if the image endpoint is unreachable
        await message.reply_text(
            script.WELCOME_TXT.format(first_name=user.first_name or "there"),
            reply_markup=main_menu_markup(),
            disable_web_page_preview=True,
        )


@Client.on_message(filters.command("help") & filters.private)
async def help_cmd(client: Client, message: Message):
    await message.reply_text(
        script.HELP_TXT,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]]),
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command("about") & filters.private)
async def about_cmd(client: Client, message: Message):
    await message.reply_text(
        script.ABOUT_TXT,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]]),
        disable_web_page_preview=True,
    )

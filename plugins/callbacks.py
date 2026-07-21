from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from database.db import db
from info import PICS_URL
from plugins.profile import build_profile_text
from plugins.start import main_menu_markup
from script import script
from utils import get_welcome_image


@Client.on_callback_query(filters.regex(r"^main_menu$"))
async def main_menu_cb(client: Client, query: CallbackQuery):
    try:
        await query.message.edit_text(
            script.WELCOME_TXT.format(first_name=query.from_user.first_name or "there"),
            reply_markup=main_menu_markup(),
        )
    except Exception:
        await query.message.reply_text(
            script.WELCOME_TXT.format(first_name=query.from_user.first_name or "there"),
            reply_markup=main_menu_markup(),
        )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^help_menu$"))
async def help_menu_cb(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        script.HELP_TXT,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]]),
    )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^about_menu$"))
async def about_menu_cb(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        script.ABOUT_TXT,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]]),
        disable_web_page_preview=True,
    )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^premium_info$"))
async def premium_info_cb(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        script.PREMIUM_TXT,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]]),
    )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^my_profile$"))
async def my_profile_cb(client: Client, query: CallbackQuery):
    text = await build_profile_text(client, query.from_user)
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]]),
    )
    await query.answer()

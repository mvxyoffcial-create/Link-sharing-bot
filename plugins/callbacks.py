from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from database.db import db
from info import PICS_URL, ADMIN_ID, FREE_USER_CHANNEL_LIMIT, FREE_PROPERTY_DURATION_HOURS
from plugins.profile import build_profile_text
from plugins.start import main_menu_markup
from script import script
from utils import get_welcome_image, temp, paginate
from datetime import datetime


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
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Premium Info", callback_data="premium_info")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]),
        disable_web_page_preview=True,
    )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^about_menu$"))
async def about_menu_cb(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        script.ABOUT_TXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]),
        disable_web_page_preview=True,
    )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^premium_info$"))
async def premium_info_cb(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        script.PREMIUM_TXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Subscribe Now", callback_data="subscribe_premium")],
            [InlineKeyboardButton("📞 Contact Admin", url=f"tg://user?id={ADMIN_ID}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]),
        disable_web_page_preview=True,
    )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^my_profile$"))
async def my_profile_cb(client: Client, query: CallbackQuery):
    text = await build_profile_text(client, query.from_user)
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 My Listings", callback_data="my_listings")],
            [InlineKeyboardButton("💎 Premium Info", callback_data="premium_info")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]),
    )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^my_listings$"))
async def my_listings_cb(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    listings = await db.channels_by_owner(user_id)
    
    if not listings:
        await query.answer("📭 You haven't added any listings yet.", show_alert=True)
        return
    
    text = "📊 **Your Listings**\n\n"
    for i, listing in enumerate(listings[:10], 1):
        status = "✅ Approved" if listing.get('approved', False) else "⏳ Pending"
        if listing.get('approved', False) and not listing.get('is_premium', False):
            expires_at = listing.get('expires_at')
            if expires_at:
                if isinstance(expires_at, str):
                    expires_at = datetime.fromisoformat(expires_at)
                if datetime.now() > expires_at:
                    status = "⏰ Expired"
        
        badge = "⭐" if listing.get('is_premium', False) else "📢"
        text += f"{i}. {badge} <b>{listing['channel_name']}</b>\n"
        text += f"   📂 {listing.get('category', 'N/A')}\n"
        text += f"   📊 {status}\n\n"
    
    if len(listings) > 10:
        text += f"\n... and {len(listings) - 10} more listings."
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add New Listing", callback_data="add_listing")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]),
        disable_web_page_preview=True
    )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^subscribe_premium$"))
async def subscribe_premium_cb(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        "💳 **Subscribe to Premium**\n\n"
        "Choose your plan:\n\n"
        "📅 **1 Month** - $5\n"
        "📅 **3 Months** - $12 (Save 20%)\n"
        "📅 **6 Months** - $20 (Save 33%)\n"
        "📅 **1 Year** - $35 (Save 42%)\n\n"
        "✨ **Premium Benefits:**\n"
        "• Unlimited listing additions\n"
        "• Listings never expire\n"
        "• Priority admin approval (within 1 hour)\n"
        "• Featured listing option\n"
        "• Priority support\n\n"
        "To subscribe, contact admin:\n"
        f"👨‍💻 <a href='tg://user?id={ADMIN_ID}'>Click here to contact admin</a>\n\n"
        "Send payment proof to admin after payment.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 Contact Admin", url=f"tg://user?id={ADMIN_ID}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="premium_info")]
        ]),
        disable_web_page_preview=True
    )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^top_listings$"))
async def top_listings_cb(client: Client, query: CallbackQuery):
    top = await db.top_channels(10)
    if not top:
        await query.answer("No listings yet.", show_alert=True)
        return
    
    text = "🏆 **Top Listings**\n\n"
    for i, c in enumerate(top, 1):
        badge = "⭐" if c.get('is_premium', False) else "✅"
        joins = c.get('joins', 0)
        text += f"{i}. {badge} <b>{c['channel_name']}</b>\n"
        text += f"   📊 {joins} joins\n\n"
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📂 Browse Categories", callback_data="browse_categories")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]),
        disable_web_page_preview=True
    )
    await query.answer()

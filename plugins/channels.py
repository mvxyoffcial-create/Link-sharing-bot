from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from database.db import db
from info import FREE_USER_CHANNEL_LIMIT, LOG_CHANNEL, PAGE_SIZE, ADMIN_ID, FREE_PROPERTY_DURATION_HOURS
from script import script
from utils import temp, paginate
from datetime import datetime, timedelta

STEP_NAME, STEP_LINK, STEP_CATEGORY, STEP_DESC = "name", "link", "category", "description"


def in_conversation(_, __, message: Message):
    return bool(message.from_user) and message.from_user.id in temp.CONVERSATION


in_add_flow = filters.create(in_conversation)


# Helper function to check if user can add listing
async def can_user_add_listing(user_id):
    """Check if user can add a listing"""
    is_premium = await db.is_premium(user_id)
    
    if is_premium:
        return True, "Premium user - unlimited"
    
    # Check total listings limit
    count = await db.user_channel_count(user_id)
    if count >= FREE_USER_CHANNEL_LIMIT:
        return False, f"Free users can add only {FREE_USER_CHANNEL_LIMIT} listing. Upgrade to premium for unlimited!"
    
    return True, "OK"

# --------------------------------------------------------------------- START
@Client.on_callback_query(filters.regex(r"^add_listing$"))
async def add_listing_start(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    is_premium = await db.is_premium(user_id)
    
    # Check if user can add listing
    can_add, reason = await can_user_add_listing(user_id)
    
    if not can_add:
        await query.answer(
            f"⚠️ {reason}\n\n💡 Get premium for unlimited additions!",
            show_alert=True,
        )
        return
    
    # Premium user - no verification needed
    temp.CONVERSATION[user_id] = {"step": STEP_NAME, "data": {}}
    await query.message.edit_text(script.SUBMIT_CHANNEL_TXT)
    await query.answer()


@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_flow(client: Client, message: Message):
    if message.from_user.id in temp.CONVERSATION:
        del temp.CONVERSATION[message.from_user.id]
        await message.reply_text("❌ Cancelled.")
    else:
        await message.reply_text("Nothing to cancel.")


# ------------------------------------------------------------------- STEPS
@Client.on_message(filters.private & filters.text & in_add_flow & ~filters.command("cancel"))
async def add_listing_steps(client: Client, message: Message):
    user_id = message.from_user.id
    convo = temp.CONVERSATION[user_id]
    step = convo["step"]
    text = message.text.strip()

    if step == STEP_NAME:
        convo["data"]["name"] = text[:100]
        convo["step"] = STEP_LINK
        await message.reply_text(
            "🔗 Great! Now send the <b>Telegram link</b> "
            "(e.g. https://t.me/yourchannel or @yourchannel)."
        )
        return

    if step == STEP_LINK:
        if not (text.startswith("https://t.me/") or text.startswith("@")):
            await message.reply_text("⚠️ That doesn't look like a valid Telegram link. Try again.")
            return
        convo["data"]["link"] = text
        convo["step"] = STEP_CATEGORY
        categories = await db.all_categories()
        buttons = [
            [InlineKeyboardButton(f"{c['icon']} {c['category_name']}", callback_data=f"addcat_{c['category_name']}")]
            for c in categories
        ]
        await message.reply_text("📂 Choose a category:", reply_markup=InlineKeyboardMarkup(buttons))
        return

    if step == STEP_DESC:
        convo["data"]["description"] = "" if text.lower() == "skip" else text[:300]
        await finalize_submission(client, message, user_id)
        return


@Client.on_callback_query(filters.regex(r"^addcat_"))
async def add_listing_category_chosen(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    if user_id not in temp.CONVERSATION:
        await query.answer("Session expired, please start again with ➕ Add Your Channel.", show_alert=True)
        return
    category = query.data.split("_", 1)[1]
    temp.CONVERSATION[user_id]["data"]["category"] = category
    temp.CONVERSATION[user_id]["step"] = STEP_DESC
    await query.message.edit_text(
        "📝 Send a short <b>description</b> (or send <code>skip</code>)."
    )
    await query.answer()


async def finalize_submission(client: Client, message: Message, user_id: int):
    convo = temp.CONVERSATION.pop(user_id, None)
    if not convo:
        return
    data = convo["data"]
    link = data["link"]
    username = link.split("/")[-1].lstrip("@")

    is_premium = await db.is_premium(user_id)
    
    # Check if free user already has a listing
    if not is_premium:
        count = await db.user_channel_count(user_id)
        if count >= FREE_USER_CHANNEL_LIMIT:
            await message.reply_text(
                f"⚠️ You already have {count} listing(s). Free users can only have {FREE_USER_CHANNEL_LIMIT} listing.\n"
                "💡 Upgrade to premium for unlimited listings!"
            )
            return

    resolved_chat_id = link
    try:
        chat = await client.get_chat(f"@{username}")
        resolved_chat_id = chat.id
    except:
        pass

    # Set expiration for free users (5 hours)
    expires_at = None
    if not is_premium:
        expires_at = datetime.utcnow() + timedelta(hours=FREE_PROPERTY_DURATION_HOURS)

    await db.add_channel(
        channel_id=resolved_chat_id,
        channel_name=data["name"],
        channel_link=link if link.startswith("http") else f"https://t.me/{username}",
        owner_id=user_id,
        category=data["category"],
        description=data.get("description", ""),
        verification_status="verified",
        is_premium=is_premium,
        expires_at=expires_at,
        approved=False,  # Needs admin approval
    )

    # Send admin notification for approval
    admin_text = (
        f"🔔 **New Listing - Awaiting Approval**\n\n"
        f"👤 Owner: [{message.from_user.first_name}](tg://user?id={user_id})\n"
        f"🆔 User ID: `{user_id}`\n"
        f"📢 Name: {data['name']}\n"
        f"🔗 Link: {link}\n"
        f"📂 Category: {data['category']}\n"
        f"📝 Description: {data.get('description', 'N/A')}\n"
        f"⭐ Type: {'Premium' if is_premium else 'Free'}\n"
        f"⏳ Expires: {expires_at.strftime('%Y-%m-%d %H:%M') if expires_at else 'Never'}\n\n"
        f"Approve or reject this listing:"
    )
    
    await client.send_message(
        ADMIN_ID,
        admin_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Approve", callback_data=f"approve_{resolved_chat_id}")],
            [InlineKeyboardButton("❌ Reject", callback_data=f"reject_{resolved_chat_id}")]
        ]),
        disable_web_page_preview=True
    )

    status_note = "✅ Submitted for admin approval. You'll be notified when approved!"

    if not is_premium:
        status_note += f"\n\n⏰ Free listing will expire after {FREE_PROPERTY_DURATION_HOURS} hours if not approved."

    await message.reply_text(
        script.LISTING_SUBMITTED_TXT.format(
            name=data['name'],
            category=data['category'],
            link=link,
            user_type='Premium' if is_premium else 'Free',
            status_note=status_note
        )
    )

    if LOG_CHANNEL:
        try:
            await client.send_message(
                LOG_CHANNEL,
                f"#New_Listing\n\n👤 Owner: <code>{user_id}</code>\n"
                f"📢 Name: {data['name']}\n🔗 Link: {link}\n📂 Category: {data['category']}\n"
                f"Type: {'Premium' if is_premium else 'Free'}"
                f"{'⏳ Expires: ' + expires_at.strftime('%Y-%m-%d %H:%M') if expires_at else ''}"
            )
        except Exception:
            pass


# ------------------------------------------------------------------ APPROVAL
@Client.on_callback_query(filters.regex(r"^approve_"))
async def approve_listing(client: Client, query: CallbackQuery):
    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ Unauthorized!", show_alert=True)
        return
    
    channel_id = query.data.split("_", 1)[1]
    await db.approve_channel(channel_id)
    
    # Get channel info
    channel = await db.get_channel(channel_id)
    if channel:
        owner_id = channel.get('owner_id')
        if owner_id:
            try:
                await client.send_message(
                    owner_id,
                    script.LISTING_APPROVED_TXT.format(
                        name=channel.get('channel_name', 'N/A'),
                        category=channel.get('category', 'N/A'),
                        link=channel.get('channel_link', 'N/A'),
                        user_type='Premium' if channel.get('is_premium', False) else 'Free'
                    )
                )
            except:
                pass
    
    await query.message.edit_text(
        f"✅ **Listing Approved!**\n\n"
        f"Channel ID: {channel_id}\n"
        f"Owner notified."
    )
    await query.answer("Approved!")


@Client.on_callback_query(filters.regex(r"^reject_"))
async def reject_listing(client: Client, query: CallbackQuery):
    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ Unauthorized!", show_alert=True)
        return
    
    channel_id = query.data.split("_", 1)[1]
    await db.reject_channel(channel_id)
    
    # Get channel info
    channel = await db.get_channel(channel_id)
    if channel:
        owner_id = channel.get('owner_id')
        if owner_id:
            try:
                await client.send_message(
                    owner_id,
                    script.LISTING_REJECTED_TXT.format(
                        name=channel.get('channel_name', 'N/A'),
                        category=channel.get('category', 'N/A')
                    )
                )
            except:
                pass
    
    await query.message.edit_text(
        f"❌ **Listing Rejected!**\n\n"
        f"Channel ID: {channel_id}"
    )
    await query.answer("Rejected!")


# ------------------------------------------------------------------ BROWSE
@Client.on_callback_query(filters.regex(r"^browse_categories$"))
async def browse_categories(client: Client, query: CallbackQuery):
    categories = await db.all_categories()
    if not categories:
        await query.answer("No categories yet.", show_alert=True)
        return
    buttons = [
        [InlineKeyboardButton(f"{c['icon']} {c['category_name']}", callback_data=f"cat_{c['category_name']}_1")]
        for c in categories
    ]
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="main_menu")])
    await query.message.edit_text("📂 <b>Browse Categories</b>", reply_markup=InlineKeyboardMarkup(buttons))
    await query.answer()


@Client.on_callback_query(filters.regex(r"^cat_"))
async def browse_category_listing(client: Client, query: CallbackQuery):
    _, category, page = query.data.split("_", 2)
    page = int(page)
    channels = await db.approved_channels_by_category(category)
    if not channels:
        await query.answer("No approved listings in this category yet.", show_alert=True)
        return

    page_items, total_pages, page = paginate(channels, page, PAGE_SIZE)

    lines = [f"📂 <b>{category}</b> — page {page}/{total_pages}\n"]
    buttons = []
    for c in page_items:
        badge = "⭐" if c.get('is_premium', False) else "✅"
        lines.append(f"{badge} <b>{c['channel_name']}</b>\n📝 {c.get('description') or 'No description'}\n")
        buttons.append([InlineKeyboardButton(f"🔗 Join {c['channel_name']}", callback_data=f"join_{c['channel_id']}")])

    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"cat_{category}_{page - 1}"))
    if page < total_pages:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"cat_{category}_{page + 1}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton("⬅️ Categories", callback_data="browse_categories")])

    await query.message.edit_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(buttons))
    await query.answer()


@Client.on_callback_query(filters.regex(r"^join_"))
async def join_channel(client: Client, query: CallbackQuery):
    channel_id_raw = query.data.split("_", 1)[1]
    try:
        channel_id = int(channel_id_raw)
    except ValueError:
        channel_id = channel_id_raw
    channel = await db.get_channel(channel_id)
    if not channel:
        await query.answer("Listing not found.", show_alert=True)
        return

    # Check if channel is approved and not expired
    if not channel.get('approved', False):
        await query.answer("⏳ This listing is pending approval.", show_alert=True)
        return
    
    # Check expiration
    expires_at = channel.get('expires_at')
    if expires_at:
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if datetime.utcnow() > expires_at:
            await query.answer("⏰ This listing has expired.", show_alert=True)
            return

    await db.increment_join(channel_id)
    await query.message.reply_text(f"✅ Here's your link: {channel['channel_link']}")
    await query.answer()


# ------------------------------------------------------------------- SEARCH
@Client.on_callback_query(filters.regex(r"^search_prompt$"))
async def search_prompt(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        "🔎 Send me a keyword (e.g. <code>anime</code>) as a normal message to search.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]]),
    )
    await query.answer()


@Client.on_message(filters.private & filters.text & ~filters.command(["start", "help", "about", "profile", "premium", "search", "cancel"]))
async def autofilter_keyword(client: Client, message: Message):
    keyword = message.text.strip()
    results = await db.search_approved_channels(keyword, limit=10)
    if not results:
        await message.reply_text(script.NO_RESULTS_TXT.format(keyword=keyword))
        return
    lines = [f"🔍 Found {len(results)} listing(s) for '{keyword}':\n"]
    for i, c in enumerate(results, 1):
        lines.append(f"{i}. {c['channel_name']} — {c['channel_link']}")
    await message.reply_text("\n".join(lines), disable_web_page_preview=True)

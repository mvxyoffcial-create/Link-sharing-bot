from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from database.db import db
from info import FREE_USER_CHANNEL_LIMIT, LOG_CHANNEL, PAGE_SIZE
from script import script
from utils import temp, paginate

STEP_NAME, STEP_LINK, STEP_CATEGORY, STEP_DESC = "name", "link", "category", "description"


def in_conversation(_, __, message: Message):
    return bool(message.from_user) and message.from_user.id in temp.CONVERSATION


in_add_flow = filters.create(in_conversation)


# --------------------------------------------------------------------- START
@Client.on_callback_query(filters.regex(r"^add_listing$"))
async def add_listing_start(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    count = await db.user_channel_count(user_id)
    if count >= FREE_USER_CHANNEL_LIMIT and not await db.is_premium(user_id):
        await query.answer(
            f"⚠️ Free users can add up to {FREE_USER_CHANNEL_LIMIT} listings. "
            "Get premium for unlimited additions!",
            show_alert=True,
        )
        return
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

    verification_status = "pending"
    resolved_chat_id = link  # fallback identifier if resolution fails

    try:
        chat = await client.get_chat(f"@{username}")
        resolved_chat_id = chat.id
        member = await client.get_chat_member(chat.id, user_id)
        if member.status.name.lower() in ("owner", "creator", "administrator"):
            verification_status = "verified"
    except RPCError:
        pass
    except Exception:
        pass

    await db.add_channel(
        channel_id=resolved_chat_id,
        channel_name=data["name"],
        channel_link=link if link.startswith("http") else f"https://t.me/{username}",
        owner_id=user_id,
        category=data["category"],
        description=data.get("description", ""),
        verification_status=verification_status,
    )

    status_note = (
        "✅ Verified automatically (you're an admin there)."
        if verification_status == "verified"
        else "⏳ Pending verification — an admin will review it, or make the bot an admin in your chat and resend to auto-verify."
    )

    await message.reply_text(
        "🎉 <b>Submitted!</b>\n\n"
        f"📢 Name: {data['name']}\n"
        f"📂 Category: {data['category']}\n\n"
        f"{status_note}"
    )

    if LOG_CHANNEL:
        try:
            await client.send_message(
                LOG_CHANNEL,
                f"#New_Listing\n\n👤 Owner: <code>{user_id}</code>\n"
                f"📢 Name: {data['name']}\n🔗 Link: {link}\n📂 Category: {data['category']}\n"
                f"Status: {verification_status}",
            )
        except Exception:
            pass


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
    channels = await db.channels_by_category(category)
    if not channels:
        await query.answer("No listings in this category yet.", show_alert=True)
        return

    page_items, total_pages, page = paginate(channels, page, PAGE_SIZE)

    lines = [f"📂 <b>{category}</b> — page {page}/{total_pages}\n"]
    buttons = []
    for c in page_items:
        badge = "✅" if c.get("verification_status") == "verified" else "⏳"
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

    is_premium = await db.is_premium(query.from_user.id)
    if not is_premium and channel.get("verification_status") != "verified":
        await query.answer(
            "⚠️ This listing isn't verified yet. Premium users can bypass this — check 💎 Premium Info.",
            show_alert=True,
        )
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


@Client.on_message(filters.private & filters.text & filters.regex(r"(?i)^(movies?|anime|series|music|gaming|news|technology|bots?|educational)( channels?)?$"))
async def autofilter_keyword(client: Client, message: Message):
    keyword = message.text.strip()
    results = await db.search_channels(keyword, limit=10)
    if not results:
        await message.reply_text(f"🔍 No listings found for '{keyword}'.")
        return
    lines = [f"🔍 Found {len(results)} listing(s) for '{keyword}':\n"]
    for i, c in enumerate(results, 1):
        lines.append(f"{i}. {c['channel_name']} — {c['channel_link']}")
    await message.reply_text("\n".join(lines), disable_web_page_preview=True)


# -------------------------------------------------------------- TOP LISTING
@Client.on_callback_query(filters.regex(r"^top_listings$"))
async def top_listings(client: Client, query: CallbackQuery):
    top = await db.top_channels(10)
    if not top:
        await query.answer("No listings yet.", show_alert=True)
        return
    lines = ["🏆 <b>Top Listings</b>\n"]
    for i, c in enumerate(top, 1):
        lines.append(f"{i}. {c['channel_name']} — {c.get('joins', 0)} joins")
    await query.message.edit_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]]),
    )
    await query.answer()

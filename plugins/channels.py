from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from database.db import db
from info import FREE_USER_CHANNEL_LIMIT, LOG_CHANNEL, PAGE_SIZE, ADMIN_ID, VERIFICATION_API, FREE_USER_DAILY_VERIFICATIONS
from script import script
from utils import temp, paginate
import requests
import json
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
    
    # Check daily verification limit
    today_verifications = await db.get_today_verifications(user_id)
    if today_verifications >= FREE_USER_DAILY_VERIFICATIONS:
        return False, f"Daily verification limit reached ({FREE_USER_DAILY_VERIFICATIONS}/day). Upgrade to premium for unlimited!"
    
    # Check total listings limit
    count = await db.user_channel_count(user_id)
    if count >= FREE_USER_CHANNEL_LIMIT:
        return False, f"Free users can add up to {FREE_USER_CHANNEL_LIMIT} listings. Upgrade to premium for unlimited!"
    
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
    
    # Check if user needs verification (non-premium users)
    if not is_premium:
        today_verifications = await db.get_today_verifications(user_id)
        if today_verifications >= FREE_USER_DAILY_VERIFICATIONS:
            await query.answer(
                f"⚠️ Daily verification limit reached ({FREE_USER_DAILY_VERIFICATIONS}/day).\n"
                "💡 Upgrade to premium for unlimited verifications!",
                show_alert=True,
            )
            return
        
        # Ask for verification first
        await query.message.edit_text(
            "🔐 **Verification Required**\n\n"
            "Before adding a listing, you need to verify.\n"
            f"📊 Free users: {FREE_USER_DAILY_VERIFICATIONS} verifications/day\n"
            "⭐ Premium users: Unlimited\n\n"
            "Click the button below to verify:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Start Verification", callback_data="start_verification")],
                [InlineKeyboardButton("💎 Get Premium", callback_data="premium_info")],
                [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
            ])
        )
        await query.answer()
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

    # Check verification status based on user type
    is_premium = await db.is_premium(user_id)
    
    if is_premium:
        verification_status = "verified"  # Premium users auto-verified
        owner_verified = True
    else:
        # Check if user has completed verification today
        has_verification = await db.has_verification_today(user_id)
        if has_verification:
            verification_status = "verified"
            owner_verified = True
            # Use one verification
            await db.use_verification(user_id)
        else:
            # Check ownership
            try:
                chat = await client.get_chat(f"@{username}")
                member = await client.get_chat_member(chat.id, user_id)
                if member.status.name.lower() in ("owner", "creator", "administrator"):
                    verification_status = "verified"
                    owner_verified = True
                else:
                    verification_status = "pending"
                    owner_verified = False
            except RPCError:
                verification_status = "pending"
                owner_verified = False
            except Exception:
                verification_status = "pending"
                owner_verified = False

    resolved_chat_id = link  # fallback identifier
    try:
        chat = await client.get_chat(f"@{username}")
        resolved_chat_id = chat.id
    except:
        pass

    # Set expiration for free users
    expires_at = None
    if not is_premium:
        expires_at = datetime.now() + timedelta(hours=24)

    await db.add_channel(
        channel_id=resolved_chat_id,
        channel_name=data["name"],
        channel_link=link if link.startswith("http") else f"https://t.me/{username}",
        owner_id=user_id,
        category=data["category"],
        description=data.get("description", ""),
        verification_status=verification_status,
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
        f"✅ Status: {verification_status}\n"
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

    status_note = (
        "✅ Verified and submitted for admin approval. You'll be notified when approved!"
        if verification_status == "verified"
        else "⏳ Pending verification — admin will review it."
    )

    if not is_premium:
        status_note += f"\n\n⏰ Free listing will expire after 24 hours if not approved."

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
                f"Status: {verification_status}\nType: {'Premium' if is_premium else 'Free'}"
                f"{'⏳ Expires: ' + expires_at.strftime('%Y-%m-%d %H:%M') if expires_at else ''}"
            )
        except Exception:
            pass


# ------------------------------------------------------------------ VERIFICATION
@Client.on_callback_query(filters.regex(r"^start_verification$"))
async def start_verification(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    is_premium = await db.is_premium(user_id)
    
    if is_premium:
        await query.answer("⭐ Premium users don't need verification!", show_alert=True)
        return
    
    # Check daily limit
    today_verifications = await db.get_today_verifications(user_id)
    if today_verifications >= FREE_USER_DAILY_VERIFICATIONS:
        await query.answer(
            f"⚠️ Daily limit reached ({FREE_USER_DAILY_VERIFICATIONS}/day).\n"
            "💡 Upgrade to premium for unlimited!",
            show_alert=True
        )
        return
    
    # Generate verification link
    verification_link = f"{VERIFICATION_API}verification_{user_id}_{int(datetime.now().timestamp())}"
    
    await query.message.edit_text(
        "🔐 **Complete Verification**\n\n"
        "Click the button below to complete verification:\n\n"
        f"📊 You have {FREE_USER_DAILY_VERIFICATIONS - today_verifications} verification(s) left today.\n"
        f"⏳ Verification is valid for 24 hours.\n\n"
        "⚠️ **Note:** You need to verify before adding any listing.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Verify Now", url=verification_link)],
            [InlineKeyboardButton("🔄 I Completed Verification", callback_data="check_verification")],
            [InlineKeyboardButton("💎 Get Premium", callback_data="premium_info")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ])
    )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^check_verification$"))
async def check_verification(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    
    # Check if user has completed verification
    if await db.has_verification_today(user_id):
        await query.answer("✅ Verification confirmed!", show_alert=True)
        await query.message.edit_text(
            "✅ **Verification Successful!**\n\n"
            "You can now add your listing.\n"
            "Click the button below to continue.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add Listing", callback_data="add_listing")],
                [InlineKeyboardButton("📋 Main Menu", callback_data="main_menu")]
            ])
        )
    else:
        # For demo, we'll simulate verification
        # In production, you'd check with the verification API
        await db.add_verification(user_id)
        await query.answer("✅ Verification completed successfully!", show_alert=True)
        await query.message.edit_text(
            "✅ **Verification Successful!**\n\n"
            "You can now add your listing.\n"
            f"📊 Remaining verifications today: {FREE_USER_DAILY_VERIFICATIONS - 1}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add Listing", callback_data="add_listing")],
                [InlineKeyboardButton("📋 Main Menu", callback_data="main_menu")]
            ])
        )


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
                    f"✅ **Your Listing Has Been Approved!**\n\n"
                    f"📢 Name: {channel.get('channel_name')}\n"
                    f"📂 Category: {channel.get('category')}\n"
                    f"🔗 Link: {channel.get('channel_link')}\n\n"
                    f"Your listing is now public! 🎉"
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
                    f"❌ **Your Listing Was Rejected**\n\n"
                    f"📢 Name: {channel.get('channel_name')}\n"
                    f"📂 Category: {channel.get('category')}\n\n"
                    f"Please contact admin for more information."
                )
            except:
                pass
    
    await query.message.edit_text(
        f"❌ **Listing Rejected!**\n\n"
        f"Channel ID: {channel_id}"
    )
    await query.answer("Rejected!")


# ------------------------------------------------------------------ BROWSE (Updated to show only approved)
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
    channels = await db.approved_channels_by_category(category)  # Only show approved
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
        if datetime.now() > expires_at:
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


@Client.on_message(filters.private & filters.text & filters.regex(r"(?i)^(movies?|anime|series|music|gaming|news|technology|bots?|educational)( channels?)?$"))
async def autofilter_keyword(client: Client, message: Message):
    keyword = message.text.strip()
    results = await db.search_approved_channels(keyword, limit=10)  # Only search approved
    if not results:
        await message.reply_text(f"🔍 No listings found for '{keyword}'.")
        return
    lines = [f"🔍 Found {len(results)} listing(s) for '{keyword}':\n"]
    for i, c in enumerate(results, 1):
        lines.append(f"{i}. {c['channel_name']} — {c['channel_link']}")
    await message.reply_text("\n".join(lines), disable_web_page_preview=True)

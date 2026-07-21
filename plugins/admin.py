import asyncio
import datetime

from pyrogram import Client, filters
from pyrogram.types import Message

from database.db import db
from info import ADMINS
from script import script

DURATION_MAP = {
    "2h": datetime.timedelta(hours=2),
    "1d": datetime.timedelta(days=1),
    "1w": datetime.timedelta(weeks=1),
    "1m": datetime.timedelta(days=30),
    "permanent": None,
}

ADMIN_HELP = (
    "🛠 <b>Admin Commands</b>\n\n"
    "/stats — bot statistics\n"
    "/broadcast &lt;message&gt; — message all users\n"
    "/add_category &lt;name&gt; — add a category\n"
    "/remove_category &lt;name&gt; — remove a category\n"
    "/add_premium &lt;user_id&gt; &lt;duration&gt; — grant premium (2h, 1d, 1w, 1m, permanent)\n"
    "/remove_premium &lt;user_id&gt; — revoke premium\n"
    "/verify_channel &lt;channel_id&gt; — manually verify a listing\n"
    "/delete_channel &lt;channel_id&gt; — remove a listing\n"
    "/admin_list — show this list"
)


@Client.on_message(filters.command("admin_list") & filters.user(ADMINS))
async def admin_list(client: Client, message: Message):
    await message.reply_text(ADMIN_HELP)


@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats_cmd(client: Client, message: Message):
    total_users = await db.total_users()
    total_premium = await db.total_premium_users()
    total_channels = await db.total_channels()
    total_categories = len(await db.all_categories())
    await message.reply_text(
        "📊 <b>Bot Statistics</b>\n\n"
        f"👥 Total Users: {total_users}\n"
        f"💎 Premium Users: {total_premium}\n"
        f"📢 Total Listings: {total_channels}\n"
        f"📂 Categories: {total_categories}"
    )


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast_cmd(client: Client, message: Message):
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text("Usage: /broadcast <message> (or reply to a message with /broadcast)")
        return

    users_cursor = await db.all_users()
    ids = [u["user_id"] async for u in users_cursor]
    status = await message.reply_text(f"📤 Broadcasting to {len(ids)} users...")

    success = failed = 0
    for uid in ids:
        try:
            if message.reply_to_message:
                await message.reply_to_message.copy(uid)
            else:
                text = message.text.split(None, 1)[1]
                await client.send_message(uid, text)
            success += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    await status.edit_text(f"✅ Broadcast done.\n\nSuccess: {success}\nFailed: {failed}")


@Client.on_message(filters.command("add_category") & filters.user(ADMINS))
async def add_category_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /add_category <name>")
        return
    name = message.text.split(None, 1)[1].strip()
    added = await db.add_category(name)
    await message.reply_text("✅ Category added." if added else "⚠️ Category already exists.")


@Client.on_message(filters.command("remove_category") & filters.user(ADMINS))
async def remove_category_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /remove_category <name>")
        return
    name = message.text.split(None, 1)[1].strip()
    removed = await db.remove_category(name)
    await message.reply_text("✅ Category removed." if removed else "⚠️ Category not found.")


@Client.on_message(filters.command("add_premium") & filters.user(ADMINS))
async def add_premium_cmd(client: Client, message: Message):
    if len(message.command) != 3:
        await message.reply_text("Usage: /add_premium <user_id> <duration>\nDuration: permanent, 2h, 1d, 1w, 1m")
        return
    try:
        user_id = int(message.command[1])
    except ValueError:
        await message.reply_text("⚠️ Invalid user_id.")
        return
    duration = message.command[2].lower()
    if duration not in DURATION_MAP:
        await message.reply_text("⚠️ Invalid duration. Use: permanent, 2h, 1d, 1w, 1m")
        return

    if duration == "permanent":
        until = datetime.datetime(2099, 1, 1)
    else:
        until = datetime.datetime.utcnow() + DURATION_MAP[duration]

    await db.set_premium(user_id, until)
    await message.reply_text(f"✅ Premium granted to <code>{user_id}</code> until {until}.")
    try:
        await client.send_message(user_id, "🎉 You've been granted Premium access! Enjoy the perks.")
    except Exception:
        pass


@Client.on_message(filters.command("remove_premium") & filters.user(ADMINS))
async def remove_premium_cmd(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /remove_premium <user_id>")
        return
    try:
        user_id = int(message.command[1])
    except ValueError:
        await message.reply_text("⚠️ Invalid user_id.")
        return
    ok = await db.remove_premium(user_id)
    if ok:
        await message.reply_text("✅ Premium removed.")
        try:
            await client.send_message(user_id, script.PREMIUM_END_TEXT.format("there"))
        except Exception:
            pass
    else:
        await message.reply_text("⚠️ That user wasn't premium.")


@Client.on_message(filters.command("verify_channel") & filters.user(ADMINS))
async def verify_channel_cmd(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /verify_channel <channel_id>")
        return
    cid = message.command[1]
    try:
        cid = int(cid)
    except ValueError:
        pass
    ok = await db.verify_channel(cid)
    await message.reply_text("✅ Verified." if ok else "⚠️ Listing not found.")


@Client.on_message(filters.command("delete_channel") & filters.user(ADMINS))
async def delete_channel_cmd(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /delete_channel <channel_id>")
        return
    cid = message.command[1]
    try:
        cid = int(cid)
    except ValueError:
        pass
    ok = await db.delete_channel(cid)
    await message.reply_text("✅ Deleted." if ok else "⚠️ Listing not found.")

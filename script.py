from info import BOT_NAME, DEVELOPER, SUPPORT_CHANNELS, FREE_USER_CHANNEL_LIMIT

SUPPORT_TXT = " | ".join(SUPPORT_CHANNELS)


class script:

    WELCOME_TXT = (
        "<b>ʜᴇʟʟᴏ, {first_name}! 👋</b>\n\n"
        "ɪ ᴀᴍ ᴀ ᴘᴏᴡᴇʀғᴜʟ <b>ᴄʜᴀɴɴᴇʟ, ɢʀᴏᴜᴘ & ʙᴏᴛ sʜᴀʀɪɴɢ ʙᴏᴛ</b> 📢\n\n"
        "▪️ ᴅɪsᴄᴏᴠᴇʀ ɴᴇᴡ ᴄʜᴀɴɴᴇʟs, ɢʀᴏᴜᴘs ᴀɴᴅ ʙᴏᴛs\n"
        "▪️ sʜᴀʀᴇ ʏᴏᴜʀ ᴏᴡɴ ᴄʜᴀɴɴᴇʟs/ɢʀᴏᴜᴘs/ʙᴏᴛs\n"
        "▪️ ᴊᴏɪɴ ᴛʜʀᴏᴜɢʜ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ sʏsᴛᴇᴍ\n"
        "▪️ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs ɢᴇᴛ ᴇxᴛʀᴀ ʙᴇɴᴇғɪᴛs! 🚀\n\n"
        f"👨‍💻 <b>Developer:</b> {DEVELOPER}\n"
        f"📢 <b>Updates:</b> {SUPPORT_TXT}"
    )

    HELP_TXT = (
        f"📖 <b>How to Use {BOT_NAME}</b>\n\n"
        "1️⃣ <b>Browse:</b> Click \"Browse Categories\"\n"
        "2️⃣ <b>Add Yours:</b> Click \"Add Channel/Group/Bot\" & verify ownership\n"
        "3️⃣ <b>Join:</b> Click \"Join\" on any listing\n"
        "4️⃣ <b>Premium:</b> Get premium for extra benefits!\n\n"
        "🔹 <b>Verification:</b> Join your own channel/group (or add the bot as admin) to verify\n"
        f"🔹 <b>Limits:</b> Free: {FREE_USER_CHANNEL_LIMIT} listings | Premium: Unlimited\n"
        f"🔹 <b>Support:</b> {SUPPORT_TXT}"
    )

    ABOUT_TXT = (
        f"╭────[ <b>About {BOT_NAME}</b> ]────⍟\n\n"
        f"├⍟ Name : {BOT_NAME}\n"
        f"├⍟ Developer : <a href='https://t.me/{DEVELOPER.lstrip('@')}'>{DEVELOPER}</a> 👨‍💻\n"
        "├⍟ Library : <a href='https://github.com/pyrogram/pyrogram'>Pyrogram</a> 📚\n"
        "├⍟ Language : <a href='https://www.python.org/'>Python 3</a> 🐍\n"
        "├⍟ Database : <a href='https://www.mongodb.com/'>MongoDB</a> 🍃\n"
        "├⍟ Version : v1.0\n"
        f"├⍟ Updates : {SUPPORT_TXT}\n"
        f"├⍟ Support : {DEVELOPER}\n"
        "╰───────────────⍟"
    )

    PREMIUM_TXT = (
        "💎 <b>Premium Benefits</b>\n\n"
        "▪️ No verification required to join listings\n"
        "▪️ Priority listing in search results\n"
        "▪️ Unlimited channel/group/bot additions\n"
        "▪️ Remove verification banner from your listings\n"
        "▪️ Direct, instant access to everything\n\n"
        "Contact an admin to purchase premium."
    )

    PREMIUM_END_TEXT = (
        "⌛️ Hey {},\n\nYour premium plan has expired. "
        "Renew it anytime to keep enjoying premium benefits!"
    )

    SUBMIT_CHANNEL_TXT = (
        "📝 <b>Submit Your Channel / Group / Bot</b>\n\n"
        "Let's get it added! First, send me the <b>name</b> you want displayed.\n\n"
        "Send /cancel anytime to stop."
    )

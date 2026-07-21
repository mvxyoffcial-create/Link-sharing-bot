from info import BOT_NAME, DEVELOPER, SUPPORT_CHANNELS, FREE_USER_CHANNEL_LIMIT, FREE_PROPERTY_DURATION_HOURS

SUPPORT_TXT = " | ".join(SUPPORT_CHANNELS)


class script:

    WELCOME_TXT = (
        "<b>ʜᴇʟʟᴏ, {first_name}! 👋</b>\n\n"
        "ɪ ᴀᴍ ᴀ ᴘᴏᴡᴇʀғᴜʟ <b>ᴄʜᴀɴɴᴇʟ, ɢʀᴏᴜᴘ & ʙᴏᴛ sʜᴀʀɪɴɢ ʙᴏᴛ</b> 📢\n\n"
        "▪️ ᴅɪsᴄᴏᴠᴇʀ ɴᴇᴡ ᴄʜᴀɴɴᴇʟs, ɢʀᴏᴜᴘs ᴀɴᴅ ʙᴏᴛs\n"
        "▪️ sʜᴀʀᴇ ʏᴏᴜʀ ᴏᴡɴ ᴄʜᴀɴɴᴇʟs/ɢʀᴏᴜᴘs/ʙᴏᴛs\n"
        "▪️ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs ɢᴇᴛ ᴇxᴛʀᴀ ʙᴇɴᴇғɪᴛs! 🚀\n\n"
        f"👨‍💻 <b>Developer:</b> {DEVELOPER}\n"
        f"📢 <b>Updates:</b> {SUPPORT_TXT}\n\n"
        f"📊 <b>Free users:</b> {FREE_USER_CHANNEL_LIMIT} listing only\n"
        f"⏰ <b>Free listings expire after {FREE_PROPERTY_DURATION_HOURS} hours</b>\n"
        f"⭐ <b>Premium:</b> Unlimited listings & no expiry!"
    )

    HELP_TXT = (
        f"📖 <b>How to Use {BOT_NAME}</b>\n\n"
        "1️⃣ <b>Browse:</b> Click \"Browse Categories\"\n"
        "2️⃣ <b>Add Yours:</b> Click \"Add Channel/Group/Bot\"\n"
        "3️⃣ <b>Join:</b> Click \"Join\" on any listing\n"
        "4️⃣ <b>Premium:</b> Get premium for extra benefits!\n\n"
        f"🔹 <b>Limits:</b> Free: {FREE_USER_CHANNEL_LIMIT} listing\n"
        f"🔹 <b>Expiry:</b> Free listings removed after {FREE_PROPERTY_DURATION_HOURS} hours\n"
        f"🔹 <b>Premium:</b> Unlimited listings, no expiry\n"
        f"🔹 <b>Admin Approval:</b> All listings need admin approval\n"
        f"🔹 <b>Support:</b> {SUPPORT_TXT}"
    )

    ABOUT_TXT = (
        f"╭────[ <b>About {BOT_NAME}</b> ]────⍟\n\n"
        f"├⍟ Name : {BOT_NAME}\n"
        f"├⍟ Developer : <a href='https://t.me/{DEVELOPER.lstrip('@')}'>{DEVELOPER}</a> 👨‍💻\n"
        "├⍟ Library : <a href='https://github.com/pyrogram/pyrogram'>Pyrogram</a> 📚\n"
        "├⍟ Language : <a href='https://www.python.org/'>Python 3</a> 🐍\n"
        "├⍟ Database : <a href='https://www.mongodb.com/'>MongoDB</a> 🍃\n"
        "├⍟ Version : v2.0 (Premium)\n"
        f"├⍟ Updates : {SUPPORT_TXT}\n"
        f"├⍟ Support : {DEVELOPER}\n"
        "╰───────────────⍟"
    )

    PREMIUM_TXT = (
        "💎 <b>Premium Benefits</b>\n\n"
        "▪️ Unlimited channel/group/bot additions\n"
        "▪️ Listings never expire\n"
        "▪️ Priority admin approval (within 1 hour)\n"
        "▪️ Featured listing option available\n"
        "▪️ Priority support\n\n"
        "📊 <b>Free vs Premium:</b>\n"
        f"• Free: {FREE_USER_CHANNEL_LIMIT} listing | expires in {FREE_PROPERTY_DURATION_HOURS} hours\n"
        "• Premium: Unlimited | No expiry\n"
        "• Premium: Instant approval\n\n"
        "💰 <b>Pricing:</b>\n"
        "• 1 Month: $5\n"
        "• 3 Months: $12 (Save 20%)\n"
        "• 6 Months: $20 (Save 33%)\n"
        "• 1 Year: $35 (Save 42%)\n\n"
        f"Contact @{DEVELOPER.lstrip('@')} to purchase premium."
    )

    PREMIUM_END_TEXT = (
        "⌛️ Hey {},\n\nYour premium plan has expired. "
        "Renew it anytime to keep enjoying premium benefits!\n\n"
        f"Contact @{DEVELOPER.lstrip('@')} to renew."
    )

    SUBMIT_CHANNEL_TXT = (
        "📝 <b>Submit Your Channel / Group / Bot</b>\n\n"
        "Let's get it added! First, send me the <b>name</b> you want displayed.\n\n"
        f"📊 <b>Free users:</b> {FREE_USER_CHANNEL_LIMIT} listing only\n"
        f"⏰ <b>Free listings expire after {FREE_PROPERTY_DURATION_HOURS} hours</b>\n"
        f"⭐ <b>Premium users:</b> Unlimited listings & never expire\n\n"
        "Send /cancel anytime to stop."
    )

    # Template strings with placeholders
    LISTING_SUBMITTED_TXT = (
        "🎉 <b>Listing Submitted!</b>\n\n"
        "📢 Name: {name}\n"
        "📂 Category: {category}\n"
        "🔗 Link: {link}\n"
        "⭐ Type: {user_type}\n\n"
        "{status_note}\n\n"
        "⏳ Wait for admin approval. You'll be notified when approved!"
    )

    LISTING_APPROVED_TXT = (
        "✅ <b>Your Listing Has Been Approved!</b>\n\n"
        "📢 Name: {name}\n"
        "📂 Category: {category}\n"
        "🔗 Link: {link}\n"
        "⭐ Type: {user_type}\n\n"
        "Your listing is now public and visible to all users! 🎉"
    )

    LISTING_REJECTED_TXT = (
        "❌ <b>Your Listing Was Rejected</b>\n\n"
        "📢 Name: {name}\n"
        "📂 Category: {category}\n\n"
        "Please contact admin for more information.\n\n"
        f"Admin: @{DEVELOPER.lstrip('@')}"
    )

    LISTING_EXPIRED_TXT = (
        "⏰ <b>Your Listing Has Expired</b>\n\n"
        "📢 Name: {name}\n"
        "📂 Category: {category}\n\n"
        f"This free listing has been automatically removed after {FREE_PROPERTY_DURATION_HOURS} hours.\n\n"
        "💡 Upgrade to premium to keep your listing active forever!\n\n"
        f"Contact @{DEVELOPER.lstrip('@')} to upgrade."
    )

    PROFILE_TXT = (
        "👤 <b>Your Profile</b>\n\n"
        "🆔 User ID: <code>{user_id}</code>\n"
        "👤 Name: {name}\n"
        "📊 Type: {user_type}\n"
        "📢 Listings: {listings}/{max_listings}\n"
        "📅 Joined: {joined_date}\n\n"
        "{premium_status}"
    )

    ADMIN_APPROVAL_TXT = (
        "🔔 <b>New Listing - Awaiting Approval</b>\n\n"
        "👤 Owner: [{owner_name}](tg://user?id={owner_id})\n"
        "🆔 User ID: <code>{owner_id}</code>\n"
        "📢 Name: {name}\n"
        "🔗 Link: {link}\n"
        "📂 Category: {category}\n"
        "📝 Description: {description}\n"
        "⭐ Type: {user_type}\n"
        "⏳ Expires: {expires}\n\n"
        "Approve or reject this listing:"
    )

    SEARCH_RESULTS_TXT = (
        "🔍 Found {count} listing(s) for '{keyword}':\n\n"
        "{results}\n\n"
        "💡 Type /search to search again."
    )

    NO_RESULTS_TXT = (
        "🔍 No listings found for '{keyword}'.\n\n"
        "Try a different keyword or browse categories."
    )

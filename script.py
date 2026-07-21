from info import BOT_NAME, DEVELOPER, SUPPORT_CHANNELS, FREE_USER_CHANNEL_LIMIT, FREE_USER_DAILY_VERIFICATIONS

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
        f"📢 <b>Updates:</b> {SUPPORT_TXT}\n\n"
        f"📊 <b>Free users:</b> {FREE_USER_DAILY_VERIFICATIONS} verifications/day\n"
        f"⏰ <b>Free listings expire after 24 hours</b>\n"
        f"⭐ <b>Premium:</b> Unlimited listings & verifications!"
    )

    HELP_TXT = (
        f"📖 <b>How to Use {BOT_NAME}</b>\n\n"
        "1️⃣ <b>Browse:</b> Click \"Browse Categories\"\n"
        "2️⃣ <b>Add Yours:</b> Click \"Add Channel/Group/Bot\" & verify ownership\n"
        "3️⃣ <b>Join:</b> Click \"Join\" on any listing\n"
        "4️⃣ <b>Premium:</b> Get premium for extra benefits!\n\n"
        "🔹 <b>Verification:</b> Join your own channel/group (or add the bot as admin) to verify\n"
        f"🔹 <b>Limits:</b> Free: {FREE_USER_CHANNEL_LIMIT} listings | {FREE_USER_DAILY_VERIFICATIONS} verifications/day\n"
        f"🔹 <b>Premium:</b> Unlimited listings & verifications\n"
        f"🔹 <b>Auto-Removal:</b> Free listings removed after 24 hours\n"
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
        "├⍟ Version : v2.0 (Premium + Verification)\n"
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
        "▪️ Direct, instant access to everything\n"
        "▪️ Listings never expire (30 days validity)\n"
        "▪️ Priority admin approval (within 1 hour)\n"
        "▪️ Featured listing option available\n\n"
        "📊 <b>Free vs Premium:</b>\n"
        f"• Free: {FREE_USER_CHANNEL_LIMIT} listings | {FREE_USER_DAILY_VERIFICATIONS} verifications/day\n"
        "• Free: 24 hour listing validity\n"
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
        f"📊 <b>Free users:</b> {FREE_USER_DAILY_VERIFICATIONS} verifications/day\n"
        f"⏰ <b>Free listings expire after 24 hours</b>\n"
        f"⭐ <b>Premium users:</b> Unlimited listings & never expire\n\n"
        "Send /cancel anytime to stop."
    )

    VERIFICATION_TXT = (
        "🔐 <b>Verification Required</b>\n\n"
        "Before adding a listing, you need to verify.\n\n"
        f"📊 <b>Free users:</b> {FREE_USER_DAILY_VERIFICATIONS} verifications/day\n"
        f"⭐ <b>Premium users:</b> Unlimited verifications\n\n"
        "Click the button below to verify your account.\n\n"
        "⚠️ <b>Note:</b> Verification is valid for 24 hours."
    )

    VERIFICATION_SUCCESS_TXT = (
        "✅ <b>Verification Successful!</b>\n\n"
        "You can now add your listing.\n\n"
        "Click the button below to continue adding your listing."
    )

    VERIFICATION_FAILED_TXT = (
        "❌ <b>Verification Failed!</b>\n\n"
        "Please try again or contact support."
    )

    LISTING_SUBMITTED_TXT = (
        "🎉 <b>Listing Submitted!</b>\n\n"
        f"📢 Name: {name}\n"
        f"📂 Category: {category}\n"
        f"🔗 Link: {link}\n"
        f"✅ Status: {status}\n"
        f"⭐ Type: {user_type}\n\n"
        f"{status_note}\n\n"
        "⏳ Wait for admin approval. You'll be notified when approved!"
    )

    LISTING_APPROVED_TXT = (
        "✅ <b>Your Listing Has Been Approved!</b>\n\n"
        f"📢 Name: {name}\n"
        f"📂 Category: {category}\n"
        f"🔗 Link: {link}\n"
        f"⭐ Type: {user_type}\n\n"
        "Your listing is now public and visible to all users! 🎉"
    )

    LISTING_REJECTED_TXT = (
        "❌ <b>Your Listing Was Rejected</b>\n\n"
        f"📢 Name: {name}\n"
        f"📂 Category: {category}\n\n"
        "Please contact admin for more information.\n\n"
        f"Admin: @{DEVELOPER.lstrip('@')}"
    )

    LISTING_EXPIRED_TXT = (
        "⏰ <b>Your Listing Has Expired</b>\n\n"
        f"📢 Name: {name}\n"
        f"📂 Category: {category}\n\n"
        "This free listing has been automatically removed after 24 hours.\n\n"
        "💡 Upgrade to premium to keep your listing active forever!\n\n"
        f"Contact @{DEVELOPER.lstrip('@')} to upgrade."
    )

    PROFILE_TXT = (
        "👤 <b>Your Profile</b>\n\n"
        f"🆔 User ID: <code>{user_id}</code>\n"
        f"👤 Name: {name}\n"
        f"📊 Type: {user_type}\n"
        f"✅ Verifications Today: {verifications}/{max_verifications}\n"
        f"📢 Listings: {listings}\n"
        f"💰 Total Verifications: {total_verifications}\n"
        f"📅 Joined: {joined_date}\n\n"
        f"{premium_status}"
    )

    ADMIN_APPROVAL_TXT = (
        "🔔 <b>New Listing - Awaiting Approval</b>\n\n"
        f"👤 Owner: [{owner_name}](tg://user?id={owner_id})\n"
        f"🆔 User ID: <code>{owner_id}</code>\n"
        f"📢 Name: {name}\n"
        f"🔗 Link: {link}\n"
        f"📂 Category: {category}\n"
        f"📝 Description: {description}\n"
        f"✅ Status: {status}\n"
        f"⭐ Type: {user_type}\n"
        f"⏳ Expires: {expires}\n"
        f"📊 Joins: {joins}\n\n"
        "Approve or reject this listing:"
    )

    LISTING_CARD_TXT = (
        "{badge} <b>{name}</b>\n"
        "📝 {description}\n"
        "🔗 <a href='{link}'>Join Now</a>\n"
        "📂 Category: {category}\n"
        f"⭐ {user_type}\n"
        f"👤 Owner: {owner}\n"
        f"📊 Joins: {joins}"
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

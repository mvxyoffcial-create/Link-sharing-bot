import datetime
import motor.motor_asyncio
from bson import ObjectId

from info import MONGO_URI, DB_NAME, DEFAULT_CATEGORIES, FREE_USER_DAILY_VERIFICATIONS


class Database:
    def __init__(self, uri: str, database_name: str):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]

        self.users = self.db.users
        self.channels = self.db.channels
        self.categories = self.db.categories
        self.verifications = self.db.verifications
        self.settings = self.db.settings

    # ---------------------------------------------------------------- USERS
    async def add_user(self, user_id: int, first_name: str = "", last_name: str = "", username: str = ""):
        if await self.users.find_one({"user_id": user_id}):
            return
        await self.users.insert_one({
            "user_id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "premium_until": None,
            "joined_date": datetime.datetime.utcnow(),
            "total_verifications": 0,
        })

    async def register_user(self, user_id: int, username: str = "", first_name: str = ""):
        """Register or update user"""
        if await self.users.find_one({"user_id": user_id}):
            await self.users.update_one(
                {"user_id": user_id},
                {"$set": {
                    "username": username,
                    "first_name": first_name,
                    "last_seen": datetime.datetime.utcnow()
                }}
            )
            return
        await self.add_user(user_id, first_name, "", username)

    async def get_user(self, user_id: int):
        return await self.users.find_one({"user_id": user_id})

    async def total_users(self) -> int:
        return await self.users.count_documents({})

    async def all_users(self):
        return self.users.find({})

    async def set_premium(self, user_id: int, until: datetime.datetime | None):
        await self.users.update_one(
            {"user_id": user_id}, {"$set": {"premium_until": until}}, upsert=True
        )

    async def remove_premium(self, user_id: int) -> bool:
        user = await self.users.find_one({"user_id": user_id})
        if not user or not user.get("premium_until"):
            return False
        await self.users.update_one({"user_id": user_id}, {"$set": {"premium_until": None}})
        return True

    async def is_premium(self, user_id: int) -> bool:
        user = await self.users.find_one({"user_id": user_id})
        if user and user.get("premium_until"):
            if user["premium_until"] > datetime.datetime.utcnow():
                return True
        return False

    async def total_premium_users(self) -> int:
        return await self.users.count_documents(
            {"premium_until": {"$gt": datetime.datetime.utcnow()}}
        )

    # ------------------------------------------------------------ VERIFICATIONS
    async def add_verification(self, user_id: int):
        """Add a verification record for today"""
        today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        await self.verifications.insert_one({
            "user_id": user_id,
            "date": today,
            "timestamp": datetime.datetime.utcnow()
        })
        await self.users.update_one(
            {"user_id": user_id},
            {"$inc": {"total_verifications": 1}}
        )

    async def get_today_verifications(self, user_id: int) -> int:
        """Get number of verifications today for a user"""
        today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + datetime.timedelta(days=1)
        count = await self.verifications.count_documents({
            "user_id": user_id,
            "date": {"$gte": today, "$lt": tomorrow}
        })
        return count

    async def has_verification_today(self, user_id: int) -> bool:
        """Check if user has verified today"""
        count = await self.get_today_verifications(user_id)
        return count > 0

    async def use_verification(self, user_id: int):
        """Use one verification (for free users)"""
        # This is called when a free user submits a listing
        # It doesn't create a new verification, just checks if they have one
        pass

    async def get_max_verifications(self, user_id: int) -> int:
        """Get max verifications for user"""
        if await self.is_premium(user_id):
            return 999999  # Unlimited for premium
        return FREE_USER_DAILY_VERIFICATIONS

    async def can_add_listing(self, user_id: int):
        """Check if user can add a listing"""
        is_premium = await self.is_premium(user_id)
        
        if is_premium:
            return True, "Premium user - unlimited"
        
        # Check daily verification limit
        today_verifications = await self.get_today_verifications(user_id)
        if today_verifications < 1:
            return False, "Please complete verification first"
        
        return True, "OK"

    # ------------------------------------------------------------- CHANNELS
    async def add_channel(self, channel_id, channel_name, channel_link, owner_id,
                           category, description="", verification_status="pending",
                           is_premium=False, expires_at=None, approved=False):
        """Add a new channel/group/bot listing"""
        await self.channels.insert_one({
            "channel_id": channel_id,
            "channel_name": channel_name,
            "channel_link": channel_link,
            "owner_id": owner_id,
            "category": category,
            "description": description,
            "is_active": True,
            "added_date": datetime.datetime.utcnow(),
            "verification_status": verification_status,
            "is_premium": is_premium,
            "expires_at": expires_at,
            "approved": approved,
            "joins": 0,
        })

    async def get_channel(self, channel_id):
        return await self.channels.find_one({"channel_id": channel_id})

    async def get_channel_by_oid(self, oid):
        return await self.channels.find_one({"_id": ObjectId(oid)})

    async def delete_channel(self, channel_id) -> bool:
        res = await self.channels.delete_one({"channel_id": channel_id})
        return res.deleted_count > 0

    async def verify_channel(self, channel_id) -> bool:
        res = await self.channels.update_one(
            {"channel_id": channel_id}, {"$set": {"verification_status": "verified"}}
        )
        return res.modified_count > 0

    async def approve_channel(self, channel_id) -> bool:
        """Approve a channel listing"""
        res = await self.channels.update_one(
            {"channel_id": channel_id},
            {"$set": {"approved": True, "verification_status": "verified"}}
        )
        return res.modified_count > 0

    async def reject_channel(self, channel_id) -> bool:
        """Reject a channel listing"""
        res = await self.channels.update_one(
            {"channel_id": channel_id},
            {"$set": {"approved": False, "is_active": False}}
        )
        return res.modified_count > 0

    async def approved_channels_by_category(self, category):
        """Get only approved channels in a category"""
        query = {
            "category": category,
            "is_active": True,
            "approved": True,
            "$or": [
                {"expires_at": None},
                {"expires_at": {"$gt": datetime.datetime.utcnow()}}
            ]
        }
        return [c async for c in self.channels.find(query).sort("added_date", -1)]

    async def channels_by_category(self, category, active_only=True):
        query = {"category": category}
        if active_only:
            query["is_active"] = True
        return [c async for c in self.channels.find(query).sort("added_date", -1)]

    async def channels_by_owner(self, owner_id):
        return [c async for c in self.channels.find({"owner_id": owner_id})]

    async def user_channel_count(self, owner_id) -> int:
        return await self.channels.count_documents({"owner_id": owner_id})

    async def total_channels(self) -> int:
        return await self.channels.count_documents({})

    async def search_channels(self, keyword: str, limit: int = 10):
        regex = {"$regex": keyword, "$options": "i"}
        cursor = self.channels.find(
            {"$or": [{"channel_name": regex}, {"description": regex}, {"category": regex}]}
        ).limit(limit)
        return [c async for c in cursor]

    async def search_approved_channels(self, keyword: str, limit: int = 10):
        """Search only approved channels"""
        regex = {"$regex": keyword, "$options": "i"}
        cursor = self.channels.find({
            "$and": [
                {"approved": True},
                {"is_active": True},
                {"$or": [{"channel_name": regex}, {"description": regex}, {"category": regex}]},
                {"$or": [
                    {"expires_at": None},
                    {"expires_at": {"$gt": datetime.datetime.utcnow()}}
                ]}
            ]
        }).limit(limit)
        return [c async for c in cursor]

    async def increment_join(self, channel_id):
        await self.channels.update_one({"channel_id": channel_id}, {"$inc": {"joins": 1}})

    async def top_channels(self, limit: int = 10):
        cursor = self.channels.find({
            "is_active": True,
            "approved": True,
            "$or": [
                {"expires_at": None},
                {"expires_at": {"$gt": datetime.datetime.utcnow()}}
            ]
        }).sort("joins", -1).limit(limit)
        return [c async for c in cursor]

    async def get_expired_properties(self, hours=24):
        """Get expired free properties"""
        expiry_time = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
        cursor = self.channels.find({
            "is_premium": False,
            "approved": True,
            "added_date": {"$lt": expiry_time}
        })
        return [c async for c in cursor]

    async def delete_expired_properties(self, hours=24):
        """Delete expired free properties"""
        expiry_time = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
        res = await self.channels.delete_many({
            "is_premium": False,
            "approved": True,
            "added_date": {"$lt": expiry_time}
        })
        return res.deleted_count

    # ------------------------------------------------------------ CATEGORIES
    async def ensure_default_categories(self):
        if await self.categories.count_documents({}) == 0:
            docs = [{"category_name": name, "icon": "📂", "is_active": True} for name in DEFAULT_CATEGORIES]
            await self.categories.insert_many(docs)

    async def add_category(self, name: str, icon: str = "📂") -> bool:
        if await self.categories.find_one({"category_name": name}):
            return False
        await self.categories.insert_one({"category_name": name, "icon": icon, "is_active": True})
        return True

    async def remove_category(self, name: str) -> bool:
        res = await self.categories.delete_one({"category_name": name})
        return res.deleted_count > 0

    async def all_categories(self):
        return [c async for c in self.categories.find({"is_active": True})]

    # ------------------------------------------------------------ SETTINGS
    async def get_setting(self, key: str):
        setting = await self.settings.find_one({"key": key})
        return setting.get("value") if setting else None

    async def set_setting(self, key: str, value):
        await self.settings.update_one(
            {"key": key},
            {"$set": {"value": value}},
            upsert=True
        )


db = Database(MONGO_URI, DB_NAME)

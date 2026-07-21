import datetime
import motor.motor_asyncio

from info import MONGO_URI, DB_NAME, DEFAULT_CATEGORIES


class Database:
    def __init__(self, uri: str, database_name: str):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]

        self.users = self.db.users
        self.channels = self.db.channels
        self.categories = self.db.categories

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
        })

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

    # ------------------------------------------------------------- CHANNELS
    async def add_channel(self, channel_id, channel_name, channel_link, owner_id,
                           category, description="", verification_status="pending"):
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
            "joins": 0,
        })

    async def get_channel(self, channel_id):
        return await self.channels.find_one({"channel_id": channel_id})

    async def get_channel_by_oid(self, oid):
        from bson import ObjectId
        return await self.channels.find_one({"_id": ObjectId(oid)})

    async def delete_channel(self, channel_id) -> bool:
        res = await self.channels.delete_one({"channel_id": channel_id})
        return res.deleted_count > 0

    async def verify_channel(self, channel_id) -> bool:
        res = await self.channels.update_one(
            {"channel_id": channel_id}, {"$set": {"verification_status": "verified"}}
        )
        return res.modified_count > 0

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

    async def increment_join(self, channel_id):
        await self.channels.update_one({"channel_id": channel_id}, {"$inc": {"joins": 1}})

    async def top_channels(self, limit: int = 10):
        cursor = self.channels.find({"is_active": True}).sort("joins", -1).limit(limit)
        return [c async for c in cursor]

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


db = Database(MONGO_URI, DB_NAME)

from motor.motor_asyncio import AsyncIOMotorDatabase
from schemas.user import UserCreate, UserInDB
from core.security import get_password_hash

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.users

    async def get_user_by_email(self, email: str):
        return await self.collection.find_one({"email": email})

    async def create_user(self, user_in: UserCreate):
        user_dict = {
            "email": user_in.email,
            "hashed_password": get_password_hash(user_in.password)
        }
        await self.collection.insert_one(user_dict)
        return user_dict
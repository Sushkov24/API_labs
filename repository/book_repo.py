from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId


class BookRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.books

    async def get_all(self, skip: int = 0, limit: int = 10, status: str = None, author: str = None) -> List[dict]:
        query = {}

        # Фільтрація в стилі MongoDB (словники)
        if status:
            query["status"] = status
        if author:
            query["author"] = {"$regex": author, "$options": "i"}

        # У Motor find() повертає курсор
        cursor = self.collection.find(query).skip(skip).limit(limit)
        books = await cursor.to_list(length=limit)
        return books

    async def get_count(self, status: str = None, author: str = None) -> int:
        query = {}
        if status:
            query["status"] = status
        if author:
            query["author"] = {"$regex": author, "$options": "i"}

        return await self.collection.count_documents(query)

    async def add(self, book_data: dict) -> dict:
        result = await self.collection.insert_one(book_data)
        # Додаємо згенерований _id в наш словник, щоб повернути його
        book_data["_id"] = result.inserted_id
        return book_data

    async def get_by_id(self, book_id: str) -> Optional[dict]:
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            return None

        return await self.collection.find_one({"_id": obj_id})

    async def delete(self, book_id: str) -> bool:
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            return False

        result = await self.collection.delete_one({"_id": obj_id})
        return result.deleted_count > 0
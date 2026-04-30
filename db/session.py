import os
from motor.motor_asyncio import AsyncIOMotorClient

# Отримуємо URL
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_admin:password@127.0.0.1:27017")

class Database:
    client: AsyncIOMotorClient = None

# Створюємо порожній об'єкт (холдер), клієнт додамо пізніше
db = Database()

async def get_db():
    """
    Dependency, який надає доступ до бази даних 'books'.
    """
    return db.client.books
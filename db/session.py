import os
import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient

# Отримуємо URL для MongoDB та Redis з екологічних змінних
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_admin:password@127.0.0.1:27017")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

class Database:
    client: AsyncIOMotorClient = None

# Створюємо порожній об'єкт (холдер) для MongoDB
db = Database()

# Ініціалізація Redis клієнта [cite: 14, 15]
# decode_responses=True дозволяє отримувати дані у вигляді рядків, а не байтів
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def get_db():
    """
    Dependency, який надає доступ до бази даних 'books'.
    """
    return db.client.books
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Отримуємо URL з середовища (з нашого docker-compose)
# Якщо запускаємо локально без докера, використовуємо localhost
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_admin:password@localhost:27017")

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def get_db():
    """
    Dependency, який надає доступ до бази даних 'books'.
    У Motor ми просто повертаємо об'єкт бази даних.
    """
    # Ми звертаємось до бази 'books', як зазначено в методичці
    return db.client.books

def init_db():
    """
    Ініціалізація клієнта.
    Саме підключення до MongoDB відбудеться автоматично
    при першому зверненні, тому складні цикли з retries
    тут зазвичай не потрібні так, як у Postgres.
    """
    db.client = AsyncIOMotorClient(MONGO_URL)
    print("Клієнт MongoDB ініціалізований")
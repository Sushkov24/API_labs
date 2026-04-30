from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient

from api.books import router as books_router
from api.auth import router as auth_router
from db.session import db, MONGO_URL


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Виконується при старті ---
    # Ініціалізуємо клієнт ТІЛЬКИ коли event loop вже працює
    db.client = AsyncIOMotorClient(MONGO_URL)

    try:
        # Пінгуємо базу для перевірки зв'язку
        await db.client.admin.command('ping')
        print("✅ Підключення до MongoDB успішне!")
    except Exception as e:
        print(f"❌ Помилка підключення до MongoDB: {e}")

    yield  # Тут сервер працює і обробляє запити (або тести виконуються)

    # --- Виконується при зупинці ---
    db.client.close()
    print("✅ Клієнт MongoDB закрито")


app = FastAPI(
    title="Library API",
    description="API для управління книгами з JWT авторизацією (Lab 6)",
    version="1.0.0",
    lifespan=lifespan  # <--- Передаємо наш lifespan сюди
)

# Підключаємо маршрути
app.include_router(books_router)
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Secure Library API (FastAPI)!"}
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.books import router as books_router
from db.session import init_db, db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ініціалізуємо AsyncIOMotorClient
    init_db()
    print("Підключення до MongoDB ініціалізовано")

    yield

    # Закриваємо з'єднання з базою, коли додаток вимикається
    if db.client:
        db.client.close()
        print("Підключення до MongoDB закрито")


app = FastAPI(title="Library API MongoDB Lab 4", lifespan=lifespan)

app.include_router(books_router)
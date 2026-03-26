from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.books import router as books_router
from db.session import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Те, що виконується при СТАРТІ сервера:
    init_db()  # Створює таблиці в Postgres
    yield

app = FastAPI(title="Library API Lab 3", lifespan=lifespan)

app.include_router(books_router)
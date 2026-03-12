from fastapi import FastAPI
from api.books import router as books_router
from db.session import init_db

app = FastAPI(title="Library API Lab 2")

@app.on_event("startup")
def on_startup():
    # Створює таблиці в Postgres
    init_db()

app.include_router(books_router)
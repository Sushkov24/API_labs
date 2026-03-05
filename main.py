from fastapi import FastAPI
from api.books import router as books_router

app = FastAPI(
    title="Library API",
    description="API для управління бібліотекою",
    version="1.0.0"
)

app.include_router(books_router)

if __name__ == "__main__":
    import uvicorn
    # Запуск сервера
    uvicorn.run("main:app", host="127.0.0.0", port=8000, reload=True)
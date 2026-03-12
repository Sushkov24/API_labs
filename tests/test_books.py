import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app  # Твій основний файл з FastAPI
from db.base import Base  # Базовий клас моделей для створення таблиць
from db.session import get_db  # Залежність, яку ми будемо підміняти

# 1. Налаштовуємо тестову базу даних у пам'яті (SQLite)
# Вона надзвичайно швидка і не зберігає дані після завершення тестів
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 2. Функція, яка підмінить реальну базу на тестову
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Говоримо FastAPI: "Коли хтось просить get_db, давай їм override_get_db"
app.dependency_overrides[get_db] = override_get_db

# Клієнт для імітації браузера/запитів
client = TestClient(app)


# 3. Фікстура: створює порожні таблиці перед кожним тестом і видаляє їх після
@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# --- САМІ ТЕСТИ ---

def test_create_book():
    """Перевіряємо, чи працює створення книги"""
    response = client.post(
        "/books/",
        json={
            "title": "Тестова книга",
            "author": "Тестовий автор",
            "description": "Перевірка тестів",
            "year": 2024,
            "status": "available"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Тестова книга"
    assert "id" in data  # Перевіряємо, що БД згенерувала ID


def test_get_all_books():
    """Перевіряємо, чи працює отримання списку книг"""
    # Спершу додаємо книгу в нашу порожню тестову БД
    client.post(
        "/books/",
        json={
            "title": "Книга для GET",
            "author": "Автор",
            "description": "Опис",
            "year": 2023,
            "status": "available"
        }
    )

    # Тепер пробуємо її отримати
    response = client.get("/books/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1  # Має бути рівно одна книга
    assert data[0]["title"] == "Книга для GET"
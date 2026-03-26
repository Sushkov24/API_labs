import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db.base import Base  # Базовий клас моделей для створення таблиць
from db.session import get_db  # Залежність, яку ми будемо підміняти

# 1. Налаштовуємо тестову базу даних у пам'яті (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)


# 3. Фікстура: створює порожні таблиці перед кожним тестом і видаляє їх після
@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)



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
    assert "id" in data


def test_get_all_books():
    """Перевіряємо, чи працює отримання списку книг з новою схемою CursorPaginatedResponse"""
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

    response = client.get("/books/")
    assert response.status_code == 200
    data = response.json()

    #тепер книги лежать всередині ключа "books"
    assert "books" in data
    assert len(data["books"]) == 1
    assert data["books"][0]["title"] == "Книга для GET"


def test_cursor_pagination():
    """Тестуємо логіку курсорної пагінації (Лабораторна 3)"""

    # 1. Створюємо дві тестові книги
    client.post("/books/", json={"title": "Книга 1", "author": "Курсор Тестер", "year": 2024, "status": "available"})
    client.post("/books/", json={"title": "Книга 2", "author": "Курсор Тестер", "year": 2024, "status": "available"})

    # 2. Отримуємо ПЕРШУ сторінку (ліміт = 1)
    res_page1 = client.get("/books/?author=Курсор Тестер&limit=1")
    assert res_page1.status_code == 200
    data_page1 = res_page1.json()

    # Перевіряємо наявність курсора
    assert len(data_page1["books"]) == 1
    assert data_page1["next_cursor"] is not None

    book1_id = data_page1["books"][0]["id"]
    cursor = data_page1["next_cursor"]

    res_page2 = client.get(f"/books/?author=Курсор Тестер&limit=1&cursor={cursor}")
    assert res_page2.status_code == 200
    data_page2 = res_page2.json()

    assert len(data_page2["books"]) == 1
    book2_id = data_page2["books"][0]["id"]

    # Перевіряємо, що пагінація дійсно дала нам НАСТУПНУ книгу, а не ту саму
    assert book1_id != book2_id
import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.fixture
async def client():
    # 1. Явно запускаємо lifespan (підключаємо БД перед тестами)
    async with app.router.lifespan_context(app):
        # 2. Створюємо клієнт
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c
    # Коли тести завершаться, lifespan автоматично закриє підключення до БД!

pytestmark = pytest.mark.anyio

async def test_register_user_success(client):
    """Тест перевіряє успішну реєстрацію нового користувача."""
    unique_email = f"test_{uuid.uuid4()}@example.com"

    response = await client.post(
        "/auth/register",
        json={
            "email": unique_email,
            "password": "strong_password_123"
        }
    )
    assert response.status_code == 201
    assert response.json() == {"message": "User created"}


async def test_register_duplicate_email(client):
    """Тест перевіряє поведінку при спробі зареєструвати існуючий email."""
    email = f"dup_{uuid.uuid4()}@example.com"
    payload = {
        "email": email,
        "password": "password123"
    }

    # Перший запит (має пройти успішно)
    await client.post("/auth/register", json=payload)

    # Другий запит з тими ж даними (має повернути помилку)
    response = await client.post("/auth/register", json=payload)
    assert response.status_code in [400, 409]


async def test_register_invalid_data(client):
    """Тест перевіряє валідацію (відсутність пароля)."""
    response = await client.post(
        "/auth/register",
        json={
            "email": "invalid_user@example.com"
        }
    )
    assert response.status_code == 422
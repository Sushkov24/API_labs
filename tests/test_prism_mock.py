"""
Integration-тести для Prism mock-сервера.
Потребують запущеного Prism на http://localhost:4010.
Запуск: docker-compose up prism
"""
import pytest
import httpx

PRISM_BASE_URL = "http://localhost:4010"
MOCK_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20ifQ.abc123"
AUTH_HEADERS = {"Authorization": f"Bearer {MOCK_TOKEN}"}

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="module")
def prism_available() -> bool:
    """Перевіряє чи доступний Prism mock-сервер."""
    try:
        r = httpx.get(f"{PRISM_BASE_URL}/", timeout=3)
        return r.status_code == 200
    except httpx.ConnectError:
        return False


@pytest.fixture(scope="module")
async def client():
    async with httpx.AsyncClient(base_url=PRISM_BASE_URL, timeout=10) as c:
        yield c


def skip_if_unavailable(prism_available):
    if not prism_available:
        pytest.skip("Prism mock-сервер недоступний. Запустіть: docker-compose up prism")


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------

class TestRoot:
    async def test_root_returns_200(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.get("/")
        assert r.status_code == 200

    async def test_root_returns_json(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.get("/")
        data = r.json()
        assert "message" in data


# ---------------------------------------------------------------------------
# Auth: Register
# ---------------------------------------------------------------------------

class TestAuthRegister:
    async def test_register_returns_201(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.post(
            "/auth/register",
            json={"email": "newuser@example.com", "password": "password123"},
        )
        assert r.status_code == 201

    async def test_register_response_has_message(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.post(
            "/auth/register",
            json={"email": "user2@example.com", "password": "password123"},
        )
        data = r.json()
        assert "message" in data

    async def test_register_invalid_body_returns_error(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.post("/auth/register", json={})
        assert r.status_code in (400, 422)


# ---------------------------------------------------------------------------
# Auth: Login
# ---------------------------------------------------------------------------

class TestAuthLogin:
    async def test_login_returns_200(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.post(
            "/auth/login",
            data={"username": "user@example.com", "password": "password123"},
        )
        assert r.status_code == 200

    async def test_login_response_has_tokens(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.post(
            "/auth/login",
            data={"username": "user@example.com", "password": "password123"},
        )
        data = r.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data

    async def test_login_token_type_is_bearer(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.post(
            "/auth/login",
            data={"username": "user@example.com", "password": "password123"},
        )
        assert r.json()["token_type"] == "bearer"

    async def test_login_missing_credentials_returns_error(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.post("/auth/login", data={})
        assert r.status_code in (400, 422)


# ---------------------------------------------------------------------------
# Auth: Refresh
# ---------------------------------------------------------------------------

class TestAuthRefresh:
    async def test_refresh_returns_200(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.post(
            "/auth/refresh",
            json={"refresh_token": "some.refresh.token"},
        )
        assert r.status_code == 200

    async def test_refresh_returns_new_tokens(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.post(
            "/auth/refresh",
            json={"refresh_token": "some.refresh.token"},
        )
        data = r.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_missing_body_returns_error(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.post("/auth/refresh", json={})
        assert r.status_code in (400, 422)


# ---------------------------------------------------------------------------
# Books: GET /books/
# ---------------------------------------------------------------------------

class TestGetBooks:
    async def test_get_books_returns_200(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.get("/books/", headers=AUTH_HEADERS)
        assert r.status_code == 200

    async def test_get_books_response_structure(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.get("/books/", headers=AUTH_HEADERS)
        data = r.json()
        assert "books" in data
        assert "count" in data
        assert "skip" in data
        assert "limit" in data

    async def test_get_books_returns_list(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.get("/books/", headers=AUTH_HEADERS)
        assert isinstance(r.json()["books"], list)

    async def test_get_books_without_auth_returns_401(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.get("/books/")
        assert r.status_code == 401

    async def test_get_books_with_status_filter(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.get("/books/?status=available", headers=AUTH_HEADERS)
        assert r.status_code == 200

    async def test_get_books_pagination_params(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.get("/books/?skip=0&limit=5", headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = r.json()
        assert data["skip"] == 0
        assert data["limit"] == 10  # Prism повертає example value

    async def test_get_books_invalid_limit_returns_error(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.get("/books/?limit=999", headers=AUTH_HEADERS)
        assert r.status_code in (400, 422)


# ---------------------------------------------------------------------------
# Books: POST /books/
# ---------------------------------------------------------------------------

class TestCreateBook:
    async def test_create_book_returns_201(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.post(
            "/books/",
            json={"title": "Test Book", "author": "Test Author", "year": 2024},
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 201

    async def test_create_book_response_has_id(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.post(
            "/books/",
            json={"title": "Test Book", "author": "Test Author", "year": 2024},
            headers=AUTH_HEADERS,
        )
        data = r.json()
        assert "_id" in data

    async def test_create_book_response_has_all_fields(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.post(
            "/books/",
            json={"title": "Test Book", "author": "Test Author", "year": 2024},
            headers=AUTH_HEADERS,
        )
        data = r.json()
        for field in ("_id", "title", "author", "year", "status"):
            assert field in data, f"Поле '{field}' відсутнє у відповіді"

    async def test_create_book_without_auth_returns_401(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.post(
            "/books/",
            json={"title": "Test Book", "author": "Test Author", "year": 2024},
        )
        assert r.status_code == 401

    async def test_create_book_missing_required_field(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.post(
            "/books/",
            json={"title": "No Author"},
            headers=AUTH_HEADERS,
        )
        assert r.status_code in (400, 422)


# ---------------------------------------------------------------------------
# Books: GET /books/{book_id}
# ---------------------------------------------------------------------------

class TestGetBookById:
    async def test_get_book_by_id_returns_200(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.get("/books/64a1f2e3b4c5d6e7f8a9b0c1", headers=AUTH_HEADERS)
        assert r.status_code == 200

    async def test_get_book_by_id_response_structure(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.get("/books/64a1f2e3b4c5d6e7f8a9b0c1", headers=AUTH_HEADERS)
        data = r.json()
        for field in ("_id", "title", "author", "year", "status"):
            assert field in data, f"Поле '{field}' відсутнє у відповіді"

    async def test_get_book_without_auth_returns_401(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.get("/books/64a1f2e3b4c5d6e7f8a9b0c1")
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# Books: DELETE /books/{book_id}
# ---------------------------------------------------------------------------

class TestDeleteBook:
    async def test_delete_book_returns_204(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.delete("/books/64a1f2e3b4c5d6e7f8a9b0c1", headers=AUTH_HEADERS)
        assert r.status_code == 204

    async def test_delete_book_without_auth_returns_401(self, client, prism_available):
        skip_if_unavailable(prism_available)
        r = await client.delete("/books/64a1f2e3b4c5d6e7f8a9b0c1")
        assert r.status_code == 401

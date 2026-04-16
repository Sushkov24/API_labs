import pytest
from main import app, books_collection

@pytest.fixture
def client():
    """Фікстура для створення тестового клієнта Flask"""
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def setup_db():
    """Фікстура для очищення бази даних перед і після кожного тесту"""
    # Очищаємо колекцію перед тестом
    books_collection.delete_many({})

    yield
    books_collection.delete_many({})


def test_get_empty_books(client):
    """Тест отримання порожнього списку книг"""
    response = client.get('/books')
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_book(client):
    """Тест створення нової книги"""
    new_book = {
        "title": "Flask Book",
        "author": "John Doe",
        "year": 2023,
        "status": "available"
    }
    response = client.post('/books', json=new_book)

    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == "Flask Book"
    assert '_id' in data  # Перевіряємо, що MongoDB згенерувала ID


def test_get_single_book(client):
    """Тест отримання конкретної книги за ID"""
    new_book = {"title": "Get Me", "author": "Author", "year": 2020}
    post_response = client.post('/books', json=new_book)
    book_id = post_response.get_json()['_id']

    response = client.get(f'/books/{book_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == "Get Me"
    assert data['_id'] == book_id


def test_update_book(client):
    """Тест оновлення книги"""
    # 1. Створюємо книгу
    new_book = {"title": "Old Title", "author": "Author"}
    post_response = client.post('/books', json=new_book)
    book_id = post_response.get_json()['_id']

    # 2. Оновлюємо її
    update_data = {"title": "New Title", "author": "Author"}
    put_response = client.put(f'/books/{book_id}', json=update_data)

    assert put_response.status_code == 200
    assert put_response.get_json()['title'] == "New Title"


def test_delete_book(client):
    """Тест видалення книги"""
    # 1. Створюємо книгу
    new_book = {"title": "Delete Me", "author": "Author"}
    post_response = client.post('/books', json=new_book)
    book_id = post_response.get_json()['_id']

    # 2. Видаляємо її
    delete_response = client.delete(f'/books/{book_id}')
    assert delete_response.status_code == 200

    get_response = client.get(f'/books/{book_id}')
    assert get_response.status_code == 404
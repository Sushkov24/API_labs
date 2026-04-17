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
    """Очищення бази даних перед і після кожного тесту"""
    books_collection.delete_many({})
    yield
    books_collection.delete_many({})

def test_get_empty_books(client):
    """Тест отримання порожнього списку книг (з пагінацією)"""
    response = client.get('/books')
    assert response.status_code == 200
    data = response.get_json()

    # Тепер ми перевіряємо нову структуру пагінації
    assert 'books' in data
    assert 'total' in data
    assert data['books'] == []
    assert data['total'] == 0


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
    assert '_id' in data


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
    new_book = {"title": "Old Title", "author": "Author"}
    post_response = client.post('/books', json=new_book)
    book_id = post_response.get_json()['_id']

    update_data = {"title": "New Title", "author": "Author"}
    put_response = client.put(f'/books/{book_id}', json=update_data)

    assert put_response.status_code == 200
    assert put_response.get_json()['title'] == "New Title"


def test_delete_book(client):
    """Тест видалення книги"""
    new_book = {"title": "Delete Me", "author": "Author"}
    post_response = client.post('/books', json=new_book)
    book_id = post_response.get_json()['_id']

    delete_response = client.delete(f'/books/{book_id}')
    assert delete_response.status_code == 200

    get_response = client.get(f'/books/{book_id}')
    assert get_response.status_code == 404


def test_pagination(client):
    """Тест для перевірки роботи пагінації (limit та skip)"""
    # 1. Створюємо 3 тестові книги
    for i in range(3):
        client.post('/books', json={"title": f"Book {i}", "author": "Test Author"})


    res_limit = client.get('/books?limit=2')
    assert res_limit.status_code == 200
    data_limit = res_limit.get_json()

    assert data_limit['total'] == 3
    assert len(data_limit['books']) == 2
    assert data_limit['books'][0]['title'] == "Book 0"


    res_skip = client.get('/books?skip=2&limit=2')
    data_skip = res_skip.get_json()

    assert len(data_skip['books']) == 1
    assert data_skip['books'][0]['title'] == "Book 2"
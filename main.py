from flask import Flask, request
from flask_restful import Api, Resource
from flasgger import Swagger
from pymongo import MongoClient

# Імпортуємо наш новий клас-репозиторій
from book_repo_mongo import BookRepositoryMongo

app = Flask(__name__)
api = Api(app)

# Налаштування Swagger
app.config['SWAGGER'] = {
    'title': 'Library API Flask + MongoDB (Lab 5)',
    'uiversion': 3
}
swagger = Swagger(app)

# Підключення до бази даних
MONGO_URL = "mongodb://mongo_admin:password@localhost:27017"
client = MongoClient(MONGO_URL)
db = client.library_flask_db
books_collection = db.books

# Створюємо екземпляр репозиторію і передаємо йому колекцію
book_repo = BookRepositoryMongo(books_collection)

class BookListResource(Resource):
    def get(self):
        """
        Отримання списку книг з пагінацією
        ---
        tags:
          - Books
        parameters:
          - name: skip
            in: query
            type: integer
            default: 0
          - name: limit
            in: query
            type: integer
            default: 10
        responses:
          200:
            description: Список книг успішно отримано
        """
        skip = request.args.get('skip', default=0, type=int)
        limit = request.args.get('limit', default=10, type=int)

        # Викликаємо репозиторій замість бази
        result = book_repo.get_all(skip=skip, limit=limit)
        return result, 200

    def post(self):
        """
        Додавання нової книги
        ---
        tags:
          - Books
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                title:
                  type: string
                author:
                  type: string
                year:
                  type: integer
                status:
                  type: string
        responses:
          201:
            description: Книгу успішно створено
        """
        data = request.get_json()
        created_book = book_repo.create(data)
        return created_book, 201


class BookResource(Resource):
    def get(self, book_id):
        """
        Отримання книги за ID
        ---
        tags:
          - Books
        parameters:
          - name: book_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: Книгу знайдено
          404:
            description: Книгу не знайдено
        """
        book = book_repo.get_by_id(book_id)
        if book:
            return book, 200
        return {"message": "Book not found or invalid ID"}, 404

    def put(self, book_id):
        """
        Оновлення книги за ID
        ---
        tags:
          - Books
        parameters:
          - name: book_id
            in: path
            type: string
            required: true
          - in: body
            name: body
            schema:
              type: object
        responses:
          200:
            description: Книгу успішно оновлено
          404:
            description: Книгу не знайдено
        """
        data = request.get_json()
        updated_book = book_repo.update(book_id, data)
        if updated_book:
            return updated_book, 200
        return {"message": "Book not found or invalid ID"}, 404

    def delete(self, book_id):
        """
        Видалення книги за ID
        ---
        tags:
          - Books
        parameters:
          - name: book_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: Книгу видалено
          404:
            description: Книгу не знайдено
        """
        success = book_repo.delete(book_id)
        if success:
            return {"message": f"Book {book_id} deleted successfully"}, 200
        return {"message": "Book not found or invalid ID"}, 404


api.add_resource(BookListResource, '/books')
api.add_resource(BookResource, '/books/<string:book_id>')

if __name__ == '__main__':
    app.run(debug=True)
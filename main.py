from flask import Flask, request
from flask_restful import Api, Resource
from flasgger import Swagger
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
api = Api(app)

# Налаштування Flasgger для Swagger UI
app.config['SWAGGER'] = {
    'title': 'Library API Flask + MongoDB (Lab 5)',
    'uiversion': 3
}
swagger = Swagger(app)

# Підключення до MongoDB (Синхронне через PyMongo)
MONGO_URL = "mongodb://mongo_admin:password@localhost:27017"
client = MongoClient(MONGO_URL)
db = client.library_flask_db
books_collection = db.books

class BookListResource(Resource):
    def get(self):
        """
        Отримання списку всіх книг
        ---
        tags:
          - Books
        responses:
          200:
            description: Список книг успішно отримано
        """
        books_cursor = books_collection.find()
        books = []
        for book in books_cursor:
            # Перетворюємо ObjectId у рядок для JSON серіалізації
            book['_id'] = str(book['_id'])
            books.append(book)
        return books, 200

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
                  example: "Flask Web Development"
                author:
                  type: string
                  example: "Miguel Grinberg"
                year:
                  type: integer
                  example: 2018
                status:
                  type: string
                  example: "available"
        responses:
          201:
            description: Книгу успішно створено
        """
        data = request.get_json()
        result = books_collection.insert_one(data)
        data['_id'] = str(result.inserted_id)
        return data, 201


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
            description: Унікальний ID книги
        responses:
          200:
            description: Книгу знайдено
          404:
            description: Книгу не знайдено
          400:
            description: Некоректний формат ID
        """
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            return {"message": "Invalid book ID format"}, 400

        book = books_collection.find_one({"_id": obj_id})
        if book:
            book['_id'] = str(book['_id'])
            return book, 200
        return {"message": "Book not found"}, 404

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
          200:
            description: Книгу успішно оновлено
          404:
            description: Книгу не знайдено
        """
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            return {"message": "Invalid book ID format"}, 400

        data = request.get_json()
        result = books_collection.update_one({"_id": obj_id}, {"$set": data})

        if result.matched_count:
            data['_id'] = book_id
            return data, 200
        return {"message": "Book not found"}, 404

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
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            return {"message": "Invalid book ID format"}, 400

        result = books_collection.delete_one({"_id": obj_id})
        if result.deleted_count:
            return {"message": f"Book {book_id} deleted successfully"}, 200
        return {"message": "Book not found"}, 404


# Реєстрація маршрутів [cite: 17]
api.add_resource(BookListResource, '/books')
api.add_resource(BookResource, '/books/<string:book_id>')

if __name__ == '__main__':
    app.run(debug=True)
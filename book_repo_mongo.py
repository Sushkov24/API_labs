from bson.objectid import ObjectId


class BookRepositoryMongo:
    def __init__(self, collection):
        """Ініціалізуємо репозиторій колекцією MongoDB"""
        self.collection = collection

    def get_all(self, skip=0, limit=10):
        """Отримання списку книг з пагінацією"""
        total = self.collection.count_documents({})
        cursor = self.collection.find().skip(skip).limit(limit)

        books = []
        for book in cursor:
            book['_id'] = str(book['_id'])
            books.append(book)

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "books": books
        }

    def get_by_id(self, book_id: str):
        """Пошук однієї книги за ID"""
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            return None  # Повертаємо None, якщо ID некоректний

        book = self.collection.find_one({"_id": obj_id})
        if book:
            book['_id'] = str(book['_id'])
        return book

    def create(self, data: dict):
        """Створення нової книги"""
        result = self.collection.insert_one(data)
        data['_id'] = str(result.inserted_id)
        return data

    def update(self, book_id: str, data: dict):
        """Оновлення книги"""
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            return None

        result = self.collection.update_one({"_id": obj_id}, {"$set": data})
        if result.matched_count:
            data['_id'] = book_id
            return data
        return None

    def delete(self, book_id: str):
        """Видалення книги"""
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            return False

        result = self.collection.delete_one({"_id": obj_id})
        return result.deleted_count > 0
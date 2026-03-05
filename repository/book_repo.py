from typing import List, Dict, Optional
from uuid import UUID
from models.db import fake_db

class BookRepository:
    async def get_all(self) -> List[Dict]:
        return fake_db

    async def get_by_id(self, book_id: UUID) -> Optional[Dict]:
        for book in fake_db:
            if book["id"] == book_id:
                return book
        return None

    async def add(self, book_data: Dict) -> Dict:
        fake_db.append(book_data)
        return book_data

    async def delete(self, book_id: UUID) -> None:
        global fake_db
        # Перезаписуємо список, виключаючи книгу з вказаним ID
        fake_db = [book for book in fake_db if book["id"] != book_id]
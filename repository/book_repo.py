from sqlalchemy.orm import Session
from sqlalchemy import select
from models.book import BookModel
from uuid import UUID
from typing import List, Optional


class BookRepository:
    def __init__(self, db: Session):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 10, status=None, author=None) -> List[BookModel]:
        query = select(BookModel)

        # Фільтрація
        if status:
            query = query.where(BookModel.status == status)
        if author:
            query = query.where(BookModel.author.ilike(f"%{author}%"))

        # Пагінація (Limit/Offset)
        query = query.offset(skip).limit(limit)

        result = self.db.execute(query)
        return result.scalars().all()

    async def add(self, book_data: dict) -> BookModel:
        db_book = BookModel(**book_data)
        self.db.add(db_book)
        self.db.commit()
        self.db.refresh(db_book)
        return db_book

    async def get_by_id(self, book_id: UUID) -> Optional[BookModel]:
        return self.db.get(BookModel, book_id)

    async def delete(self, book_id: UUID) -> bool:
        book = self.db.get(BookModel, book_id)
        if book:
            self.db.delete(book)
            self.db.commit()
            return True
        return False
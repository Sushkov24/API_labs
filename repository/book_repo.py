from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.book import BookModel
from uuid import UUID
from typing import List, Optional


class BookRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 10, status=None, author=None, sort_by=None) -> List[BookModel]:
        query = select(BookModel)

        # 1. Фільтрація на рівні БД
        if status:
            query = query.where(BookModel.status == status)
        if author:
            query = query.where(BookModel.author.ilike(f"%{author}%"))

        # 2. Сортування на рівні БД
        if sort_by == "title":
            query = query.order_by(BookModel.title)
        elif sort_by == "year":
            query = query.order_by(BookModel.year)

        # 3. Пагінація
        query = query.offset(skip).limit(limit)

        result = self.db.execute(query)
        return result.scalars().all()

    def get_count(self, status=None, author=None) -> int:
        """Повертає загальну кількість книг, що відповідають фільтрам (без limit/offset)"""
        query = select(func.count(BookModel.id))

        if status:
            query = query.where(BookModel.status == status)
        if author:
            query = query.where(BookModel.author.ilike(f"%{author}%"))

        return self.db.execute(query).scalar()

    def add(self, book_data: dict) -> BookModel:
        db_book = BookModel(**book_data)
        self.db.add(db_book)
        self.db.commit()
        self.db.refresh(db_book)
        return db_book

    def get_by_id(self, book_id: UUID) -> Optional[BookModel]:
        return self.db.get(BookModel, book_id)

    def delete(self, book_id: UUID) -> bool:
        book = self.db.get(BookModel, book_id)
        if book:
            self.db.delete(book)
            self.db.commit()
            return True
        return False
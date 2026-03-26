import uuid
from typing import List, Optional
from fastapi import Request
from sqlalchemy.orm import Session
from schemas.book import BookCreate, BookResponse, BookStatus
from repository.book_repo import BookRepository

class BookService:
    def __init__(self, db: Session):
        self.repo = BookRepository(db)

    def get_books(
            self,
            request: Request,
            status: Optional[BookStatus] = None,
            author: Optional[str] = None,
            cursor: Optional[uuid.UUID] = None,
            limit: int = 10
    ) -> dict:
        db_status = status.value if status else None

        # 1. Беремо потрібну сторінку з бази даних
        db_books = self.repo.get_all(
            limit=limit,
            cursor=cursor,
            status=db_status,
            author=author
        )

        # 2. Генеруємо next_cursor та next_url
        next_cursor = None
        next_url = None
        if len(db_books) == limit and len(db_books) > 0:
            next_cursor = db_books[-1].id  # ID останньої книги в списку стає нашим курсором
            next_url = str(request.url.include_query_params(cursor=next_cursor, limit=limit))

        # 3. Конвертуємо у Pydantic схеми
        books_list = [
            BookResponse(
                id=b.id,
                title=b.title,
                author=b.author,
                description=b.description,
                year=b.year,
                status=b.status
            ) for b in db_books
        ]

        # 4. Повертаємо словник, який відповідає нашій новій CursorPaginatedResponse
        return {
            "limit": limit,
            "next_cursor": next_cursor,
            "next_url": next_url,
            "books": books_list
        }

    def get_book(self, book_id: uuid.UUID) -> Optional[BookResponse]:
        b = self.repo.get_by_id(book_id)
        if b:
            return BookResponse(
                id=b.id, title=b.title, author=b.author,
                description=b.description, year=b.year, status=b.status
            )
        return None

    def create_book(self, book_in: BookCreate) -> BookResponse:
        book_dict = book_in.model_dump()
        book_dict["id"] = uuid.uuid4()

        b = self.repo.add(book_dict)

        return BookResponse(
            id=b.id, title=b.title, author=b.author,
            description=b.description, year=b.year, status=b.status
        )

    def delete_book(self, book_id: uuid.UUID) -> None:
        self.repo.delete(book_id)
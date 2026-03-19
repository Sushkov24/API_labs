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
            sort_by: Optional[str] = None,
            skip: int = 0,
            limit: int = 10
    ) -> dict:
        # Для БД статус треба передавати як рядок (value)
        db_status = status.value if status else None

        # 1. Рахуємо загальну кількість для пагінації
        total_count = self.repo.get_count(status=db_status, author=author)

        # 2. Беремо потрібну сторінку з бази даних
        db_books = self.repo.get_all(
            skip=skip,
            limit=limit,
            status=db_status,
            author=author,
            sort_by=sort_by
        )

        # 3. Генеруємо next_url (Наступна сторінка)
        next_url = None
        if skip + limit < total_count:
            next_skip = skip + limit
            next_url = str(request.url.include_query_params(skip=next_skip, limit=limit))

        # --- ДОДАНО ЛОГІКУ ДЛЯ PREV_URL (Попередня сторінка) ---
        prev_url = None
        if skip > 0:
            # max(0, ...) гарантує, що skip ніколи не стане від'ємним
            prev_skip = max(0, skip - limit)
            prev_url = str(request.url.include_query_params(skip=prev_skip, limit=limit))
        # -------------------------------------------------------

        # 4. Конвертуємо у Pydantic схеми
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

        return {
            "count": total_count,
            "skip": skip,
            "limit": limit,
            "next_url": next_url,
            "prev_url": prev_url,  # <--- ДОДАНО У ВІДПОВІДЬ
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
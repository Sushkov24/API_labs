from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from schemas.book import BookCreate, BookResponse, BookStatus
from repository.book_repo import BookRepository


class BookService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = BookRepository(db)

    async def get_books(
            self,
            status: Optional[BookStatus] = None,
            author: Optional[str] = None,
            skip: int = 0,
            limit: int = 10
    ) -> dict:
        db_status = status.value if status else None

        # 1. Асинхронно рахуємо загальну кількість для пагінації
        total_count = await self.repo.get_count(status=db_status, author=author)

        # 2. Асинхронно беремо потрібну сторінку з БД
        db_books = await self.repo.get_all(
            skip=skip,
            limit=limit,
            status=db_status,
            author=author
        )

        # 3. Конвертуємо у Pydantic схеми.
        books_list = [BookResponse(**b) for b in db_books]

        # 4. Повертаємо словник, який відповідає нашій PaginatedBookResponse
        return {
            "count": total_count,
            "skip": skip,
            "limit": limit,
            "books": books_list
        }

    async def get_book(self, book_id: str) -> Optional[BookResponse]:
        b = await self.repo.get_by_id(book_id)
        if b:
            return BookResponse(**b)
        return None

    async def create_book(self, book_in: BookCreate) -> BookResponse:
        book_dict = book_in.model_dump()

        created_book = await self.repo.add(book_dict)

        return BookResponse(**created_book)

    async def delete_book(self, book_id: str) -> bool:
        return await self.repo.delete(book_id)
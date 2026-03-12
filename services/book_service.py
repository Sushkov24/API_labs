import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from schemas.book import BookCreate, BookResponse, BookStatus
from repository.book_repo import BookRepository


class BookService:
    def __init__(self, db: Session):
        self.repo = BookRepository(db)

    async def get_books(
            self,
            status: Optional[BookStatus] = None,
            author: Optional[str] = None,
            sort_by: Optional[str] = None
    ) -> List[BookResponse]:
        books_data = await self.repo.get_all()

        # Фільтрація (звертаємось через крапку, бо це об'єкти БД)
        if status:
            books_data = [b for b in books_data if b.status == status.value]
        if author:
            books_data = [b for b in books_data if author.lower() in b.author.lower()]

        # Сортування
        if sort_by == "title":
            books_data.sort(key=lambda x: x.title.lower())
        elif sort_by == "year":
            books_data.sort(key=lambda x: x.year)

        # Конвертуємо BookModel у BookResponse безпечно
        return [
            BookResponse(
                id=b.id,
                title=b.title,
                author=b.author,
                description=b.description,
                year=b.year,
                status=b.status
            ) for b in books_data
        ]

    async def get_book(self, book_id: uuid.UUID) -> Optional[BookResponse]:
        b = await self.repo.get_by_id(book_id)
        if b:
            return BookResponse(
                id=b.id,
                title=b.title,
                author=b.author,
                description=b.description,
                year=b.year,
                status=b.status
            )
        return None

    async def create_book(self, book_in: BookCreate) -> BookResponse:
        book_dict = book_in.model_dump()
        book_dict["id"] = uuid.uuid4()

        b = await self.repo.add(book_dict)

        # Передаємо атрибути напряму, без **
        return BookResponse(
            id=b.id,
            title=b.title,
            author=b.author,
            description=b.description,
            year=b.year,
            status=b.status
        )

    async def delete_book(self, book_id: uuid.UUID) -> None:
        await self.repo.delete(book_id)
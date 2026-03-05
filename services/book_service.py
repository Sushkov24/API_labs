import uuid
from typing import List, Optional
from schemas.book import BookCreate, BookResponse, BookStatus
from repository.book_repo import BookRepository


class BookService:
    def __init__(self):
        self.repo = BookRepository()

    async def get_books(
            self,
            status: Optional[BookStatus] = None,
            author: Optional[str] = None,
            sort_by: Optional[str] = None
    ) -> List[BookResponse]:
        books_data = await self.repo.get_all()

        # Фільтрація
        if status:
            books_data = [b for b in books_data if b["status"] == status.value]
        if author:
            books_data = [b for b in books_data if author.lower() in b["author"].lower()]

        # Сортування
        if sort_by == "title":
            books_data.sort(key=lambda x: x["title"].lower())
        elif sort_by == "year":
            books_data.sort(key=lambda x: x["year"])

        return [BookResponse(**b) for b in books_data]

    async def get_book(self, book_id: uuid.UUID) -> Optional[BookResponse]:
        book_data = await self.repo.get_by_id(book_id)
        if book_data:
            return BookResponse(**book_data)
        return None

    async def create_book(self, book_in: BookCreate) -> BookResponse:
        book_dict = book_in.model_dump()
        book_dict["id"] = uuid.uuid4()

        saved_book = await self.repo.add(book_dict)
        return BookResponse(**saved_book)

    async def delete_book(self, book_id: uuid.UUID) -> None:
        # Ідемпотентне видалення: якщо книги немає, помилки не буде
        await self.repo.delete(book_id)
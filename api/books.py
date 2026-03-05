from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID

from schemas.book import BookCreate, BookResponse, BookStatus
from services.book_service import BookService

router = APIRouter(prefix="/books", tags=["Books"])
book_service = BookService()

@router.get("/", response_model=List[BookResponse], status_code=status.HTTP_200_OK)
async def get_all_books(
    status_filter: Optional[BookStatus] = Query(None, alias="status", description="Фільтр по статусу"),
    author: Optional[str] = Query(None, description="Фільтр по автору (частковий збіг)"),
    sort_by: Optional[str] = Query(None, pattern="^(title|year)$", description="Сортування (title або year)")
):
    """Отримання всіх книг з можливою фільтрацією та сортуванням."""
    return await book_service.get_books(status=status_filter, author=author, sort_by=sort_by)

@router.get("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
async def get_book_by_id(book_id: UUID):
    """Отримання книги за ID."""
    book = await book_service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книгу не знайдено")
    return book

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def add_book(book: BookCreate):
    """Додавання нової книги."""
    return await book_service.create_book(book)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID):
    """Ідемпотентне видалення книги. Завжди повертає 204."""
    await book_service.delete_book(book_id)
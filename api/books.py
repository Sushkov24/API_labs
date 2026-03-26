from fastapi import APIRouter, HTTPException, status, Query, Depends, Request
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

# Змінили імпорт схеми на CursorPaginatedResponse
from schemas.book import BookCreate, BookResponse, BookStatus, CursorPaginatedResponse
from services.book_service import BookService
from db.session import get_db

router = APIRouter(prefix="/books", tags=["Books"])

# Оновили response_model
@router.get("/", response_model=CursorPaginatedResponse, status_code=status.HTTP_200_OK)
def get_all_books(
    request: Request,
    status_filter: Optional[BookStatus] = Query(default=None, alias="status", description="Фільтр по статусу"),
    author: Optional[str] = Query(default=None, description="Фільтр по автору (частковий збіг)"),
    # ДОДАЛИ КУРСОР ЗАМІСТЬ SKIP:
    cursor: Optional[UUID] = Query(default=None, description="ID останнього запису з попередньої сторінки"),
    limit: int = Query(10, ge=1, le=100, description="Скільки записів показати на сторінці"),
    db: Session = Depends(get_db)
):
    """Отримання всіх книг з можливою фільтрацією та курсорною пагінацією."""
    book_service = BookService(db)
    return book_service.get_books(
        request=request,
        status=status_filter,
        author=author,
        cursor=cursor,
        limit=limit
    )

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def add_book(book: BookCreate, db: Session = Depends(get_db)):
    """Додавання нової книги."""
    book_service = BookService(db)
    return book_service.create_book(book)

@router.get("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
def get_book_by_id(book_id: UUID, db: Session = Depends(get_db)):
    """Отримання книги за ID."""
    book_service = BookService(db)
    book = book_service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книгу не знайдено")
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: UUID, db: Session = Depends(get_db)):
    """Видалення книги за ID."""
    book_service = BookService(db)
    book = book_service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книгу не знайдено")
    book_service.delete_book(book_id)
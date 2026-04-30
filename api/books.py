from fastapi import APIRouter, HTTPException, status, Query, Depends, Request
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.book import BookCreate, BookResponse, BookStatus, PaginatedBookResponse
from services.book_service import BookService
from db.session import get_db
from core.dependencies import get_current_user
from core.rate_limiter import check_rate_limit  # Імпортуємо наш лімітер

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=PaginatedBookResponse, status_code=status.HTTP_200_OK)
async def get_all_books(
        request: Request,  # Додано для rate limiter [cite: 25, 49]
        status_filter: Optional[BookStatus] = Query(default=None, alias="status"),
        author: Optional[str] = Query(default=None),
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: AsyncIOMotorDatabase = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    # Перевірка ліміту запитів перед виконанням логіки [cite: 51]
    await check_rate_limit(request, user_email=current_user)

    book_service = BookService(db)
    return await book_service.get_books(status=status_filter, author=author, skip=skip, limit=limit)


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def add_book(
        request: Request,  # Додано для rate limiter [cite: 25]
        book: BookCreate,
        db: AsyncIOMotorDatabase = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    # Перевірка ліміту запитів [cite: 51]
    await check_rate_limit(request, user_email=current_user)

    book_service = BookService(db)
    return await book_service.create_book(book)


@router.get("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
async def get_book_by_id(
        request: Request,  # Додано для rate limiter [cite: 25]
        book_id: str,
        db: AsyncIOMotorDatabase = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    # Перевірка ліміту запитів [cite: 51]
    await check_rate_limit(request, user_email=current_user)

    book_service = BookService(db)
    book = await book_service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книгу не знайдено")
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
        request: Request,  # Додано для rate limiter [cite: 25]
        book_id: str,
        db: AsyncIOMotorDatabase = Depends(get_db),
        current_user: str = Depends(get_current_user)
):
    # Перевірка ліміту запитів [cite: 51]
    await check_rate_limit(request, user_email=current_user)

    book_service = BookService(db)
    deleted = await book_service.delete_book(book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Книгу не знайдено")
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class BookStatus(str, Enum):
    available = "available"
    borrowed = "borrowed"

class BookBase(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    year: int

class BookCreate(BookBase):
    status: BookStatus = BookStatus.available

class BookResponse(BookBase):
    id: UUID
    status: BookStatus

    class Config:
        from_attributes = True

# Нова схема для пагінації
class PaginatedBookResponse(BaseModel):
    count: int
    skip: int
    limit: int
    next_url: Optional[str] = None
    prev_url: Optional[str] = None
    books: List[BookResponse]
from enum import Enum
from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)

# Схема для курсорної пагінації (Лабораторна №3)
class CursorPaginatedResponse(BaseModel):
    limit: int
    next_cursor: Optional[UUID] = None
    next_url: Optional[str] = None
    books: List[BookResponse]
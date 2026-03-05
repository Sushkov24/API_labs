from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from enum import Enum

class BookStatus(str, Enum):
    AVAILABLE = "available"
    CHECKED_OUT = "checked_out"

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150, description="Назва книги")
    author: str = Field(..., min_length=1, max_length=100, description="Автор книги")
    description: Optional[str] = Field(None, max_length=500, description="Опис книги")
    year: int = Field(..., gt=0, description="Рік випуску")
    status: BookStatus = Field(default=BookStatus.AVAILABLE, description="Статус книги")

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: UUID
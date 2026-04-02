from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

# Імпортуємо спеціальний тип для MongoDB _id
from pydantic_mongo import ObjectIdField

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
    id: ObjectIdField = Field(alias="_id")
    status: BookStatus

    model_config = ConfigDict(
        populate_by_name=True,  # Дозволяє Pydantic розуміти і 'id', і '_id'
        from_attributes=True
    )

# Повертаємось до пагінації Limit-Offset
class PaginatedBookResponse(BaseModel):
    count: int
    skip: int
    limit: int
    books: List[BookResponse]
import uuid
from sqlalchemy import Column, String, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from db.base import Base
from schemas.book import BookStatus

class BookModel(Base):
    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    description = Column(String, nullable=True)
    year = Column(Integer, nullable=False)
    status = Column(SQLEnum(BookStatus), default=BookStatus.available)
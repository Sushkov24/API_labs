import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from db.base import Base

# Беремо URL з Docker (або локальний для тестів)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/library_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Це Dependency, який ми будемо використовувати в ендпоінтах
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функція для автоматичного створення таблиць
def init_db():
    Base.metadata.create_all(bind=engine)
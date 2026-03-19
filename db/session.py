import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
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

# Оновлена функція для автоматичного створення таблиць із повторними спробами
def init_db(max_retries=5, delay=3):
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("Успішно підключено до бази даних та створено таблиці!")
            break
        except OperationalError as e:
            print(f"База даних ще не готова. Повторна спроба через {delay} секунд... (Спроба {attempt + 1}/{max_retries})")
            time.sleep(delay)
    else:
        # Якщо цикл завершився і break не спрацював
        print("Критична помилка: Не вдалося підключитися до бази даних після кількох спроб.")
        raise Exception("База даних недоступна")
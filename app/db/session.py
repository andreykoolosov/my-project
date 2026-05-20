from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


# это мост между ORM (SQLAlchemy) и базой данных.
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False)  # создаем фабрику сессий


def get_db():
    """"Функция для инъекции сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

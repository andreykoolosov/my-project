from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings


settings = get_settings()

# это мост между ORM (SQLAlchemy) и базой данных.
engine = create_engine(settings.DATABASE_URL)
Sessionlocal = sessionmaker(bind=engine)  # создаем фабрику сессий


def get_db():
    """"Функция для инъекции сессии БД"""
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()

from app.services.task import TaskService
from app.services.category import CategoryService
from sqlalchemy.orm import Session
from app.db.session import get_db
from fastapi import Depends


def get_task_service(db: Session = Depends(get_db)):
    """"Функция для инъекции сессии БД"""
    return TaskService(db=db)


def get_category_service(db: Session = Depends(get_db)):
    return CategoryService(db=db)

from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, Session
import uvicorn
import os


# юрл подключения к БД
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://postgres:admin@localhost:15432/postgres")
# это мост между ORM (SQLAlchemy) и базой данных.
engine = create_engine(DATABASE_URL)
Sessionlocal = sessionmaker(bind=engine)  # создаем фабрику сессий


class Base(DeclarativeBase):  # родительный класс
    id: Mapped[str] = mapped_column(
        primary_key=True, default=lambda: str(uuid4()))


class TaskORM(Base):
    __tablename__ = "tasks"

    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)


class CategoryORM(Base):
    __tablename__ = "categories"

    name: Mapped[str]

# что делать при открытии и закрытии приложения
# создает таблицы от класса Base, если их еще нет


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("START")
    Base.metadata.create_all(bind=engine)
    yield
    print("END")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    # пускаем только фронт с порта 3000
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],  # разрешаем все методы (GET, POST...)
    allow_headers=["*"],  # разрешаем любые заголовки
    allow_credentials=True,  # разрешаем отправлять куки
)


class TaskSchema(BaseModel):
    id: str
    title: str
    completed: bool


class TaskCreateSchema(BaseModel):
    title: str


class TaskUpdateSchema(BaseModel):
    title: str | None = None
    completed: bool | None = None


class CategorySchema(BaseModel):
    id: str
    name: str


class CategoryCreateSchema(BaseModel):
    name: str


class CategoryUpdateSchema(BaseModel):
    name: str | None = None


def get_db():
    # Создаёт и возвращает сессию SQLAlchemy для работы с БД.
    db = Sessionlocal()
    try:
        yield db
    finally:
        # Автоматически закрывает сессию после завершения работы.
        db.close()


def task_orm_to_model(task_orm: TaskORM) -> TaskSchema:
    return TaskSchema(
        id=task_orm.id,
        title=task_orm.title,
        completed=task_orm.completed)


def category_orm_to_model(category_orm: CategoryORM) -> CategorySchema:
    return CategorySchema(
        id=category_orm.id,
        name=category_orm.name)


@app.get("/tasks", response_model=list[TaskSchema])
def read_tasks(db: Session = Depends(get_db)) -> list[TaskSchema]:
    tasks_from_db = db.scalars(select(TaskORM)).all()
    return [task_orm_to_model(task) for task in tasks_from_db]


@app.post("/tasks", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreateSchema, db: Session = Depends(get_db)) -> TaskSchema:
    new_task = TaskORM(title=payload.title, completed=False)
    db.add(new_task)
    db.commit()
    return task_orm_to_model(new_task)


@app.patch("/tasks/{task_id}", response_model=TaskSchema)
def update_task(task_id: str, payload: TaskUpdateSchema, db: Session = Depends(get_db)) -> TaskSchema:
    task_for_update = db.get(TaskORM, task_id)
    if task_for_update is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if payload.title is not None:
        task_for_update.title = payload.title
    if payload.completed is not None:
        task_for_update.completed = payload.completed
    db.commit()
    return task_orm_to_model(task_for_update)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)) -> None:
    task_for_delete = db.get(TaskORM, task_id)
    if task_for_delete is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task_for_delete)
    db.commit()


@app.get("/categories", response_model=list[CategorySchema])
def read_categories(db: Session = Depends(get_db)) -> list[CategorySchema]:
    categories_from_db = db.scalars(select(CategoryORM)).all()
    return [category_orm_to_model(cat_orm) for cat_orm in categories_from_db]


@app.post("/categories", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreateSchema, db: Session = Depends(get_db)) -> CategorySchema:
    new_category = CategoryORM(name=payload.name)
    db.add(new_category)
    db.commit()
    return category_orm_to_model(new_category)


@app.patch("/categories/{category_id}", response_model=CategorySchema)
def update_category(category_id: str, payload: CategoryUpdateSchema, db: Session = Depends(get_db)) -> CategorySchema:
    category_for_update = db.get(CategoryORM, category_id)
    if category_for_update is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if payload.name is not None:
        category_for_update.name = payload.name
    db.commit()
    return category_orm_to_model(category_for_update)


@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, db: Session = Depends(get_db)) -> None:
    category_for_delete = db.get(CategoryORM, category_id)
    if category_for_delete is None:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category_for_delete)
    db.commit()


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8080, host="0.0.0.0")

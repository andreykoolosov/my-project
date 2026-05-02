from uuid import uuid4
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


class TaskSchema(BaseModel):
    id: str
    title: str
    completed: bool


class TaskCreateSchema(BaseModel):
    title: str


tasks: list[TaskSchema] = []


@app.get("/")
def read_root():
    return {"message": "Hello World!"}


@app.get("/tasks", response_model=list[TaskSchema])
def read_tasks() -> list[TaskSchema]:
    return tasks


@app.post("/tasks", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreateSchema) -> TaskSchema:
    new_task = TaskSchema(
        id=str(uuid4()), title=payload.title, completed=False)
    tasks.append(new_task)
    return new_task


class BookCreate(BaseModel):
    book: str


book = None


@app.get("/book")
def read_book():
    return f"Любимая книга: {book}"


@app.post("/book")
def create_book(payload: BookCreate) -> str:
    global book
    book = payload.book
    return book

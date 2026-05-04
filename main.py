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


class BookCreateSchema(BaseModel):
    book: str


class TaskUpdateSchema(BaseModel):
    title: str | None = None
    completed: bool | None = None


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


@app.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdateSchema):
    for task in tasks:
        if task.id == task_id:
            if payload.title is not None:
                task.title = payload.title
            if payload.completed is not None:
                task.completed = payload.completed
            return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)
            return


book = None


@app.get("/book")
def read_book():
    return f"Любимая книга: {book}"


@app.post("/book")
def create_book(payload: BookCreateSchema) -> str:
    global book
    book = payload.book
    return book

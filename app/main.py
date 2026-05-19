from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.base import Base
from app.db.session import engine
from app.api.routers.task import router as task_router
from app.api.routers.category import router as category_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("START")
    Base.metadata.create_all(bind=engine)
    yield
    print("END")


app = FastAPI(lifespan=lifespan)
app.include_router(router=task_router)
app.include_router(router=category_router)

app.add_middleware(
    CORSMiddleware,
    # пускаем только фронт с порта 3000
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],  # разрешаем все методы (GET, POST...)
    allow_headers=["*"],  # разрешаем любые заголовки
    allow_credentials=True,  # разрешаем отправлять куки
)

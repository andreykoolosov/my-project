from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers.task import router as task_router
from app.api.routers.category import router as category_router
from app.core.config import settings


app = FastAPI()
app.include_router(router=task_router)
app.include_router(router=category_router)

app.add_middleware(
    CORSMiddleware,
    # пускаем только фронт с порта 3000
    allow_origins=[settings.CORS_ALLOWED_ORIGIN],
    allow_methods=["*"],  # разрешаем все методы (GET, POST...)
    allow_headers=["*"],  # разрешаем любые заголовки
    allow_credentials=True,  # разрешаем отправлять куки
)

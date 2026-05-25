import logging
from time import perf_counter

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.category import router as category_router
from app.api.routers.task import router as task_router
from app.core.config import settings
from app.core.logging import configure_logging

app = FastAPI()

x_request_number = 0

configure_logging()
logger = logging.getLogger("app.middleware")

app.add_middleware(
    CORSMiddleware,
    # пускаем только фронт с порта 3000
    allow_origins=[settings.CORS_ALLOWED_ORIGIN],
    allow_methods=["*"],  # разрешаем все методы (GET, POST...)
    allow_headers=["*"],  # разрешаем любые заголовки
    allow_credentials=True,  # разрешаем отправлять куки
)


@app.middleware("http")
async def my_middleware(request: Request, call_next) -> Response:
    global x_request_number
    started_at = perf_counter()
    x_request_number += 1
    try:
        response: Response = await call_next(request)
    except Exception:
        duration_ms = (perf_counter() - started_at) * 1000
        logger.exception(
            "Request failed: %s %s completed_in=%.2fms",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = (perf_counter() - started_at) * 1000
    logger.info(
        "%s %s -> %s completed_in=%.2fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    response.headers["X-Request-Number"] = str(x_request_number)
    return response


app.include_router(router=task_router)
app.include_router(router=category_router)

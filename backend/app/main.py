from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.db import Base, engine
from app.routers import tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 부팅 시 DB 스키마 자동 생성 (MVP)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="TaskFlow Pro API", version="0.1.0", lifespan=lifespan)


# 02-specs 검증 규칙: 형식 위반은 400 (FastAPI 기본 422 → 400으로 변환)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": exc.errors()})


app.include_router(tasks.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}

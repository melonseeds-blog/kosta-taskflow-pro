from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.db import Base, engine
from app.routers import tasks

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


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


# 정적 파일(frontend) 서빙은 라우터 등록 이후에 마운트
if FRONTEND_DIR.is_dir():
    app.mount(
        "/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend"
    )

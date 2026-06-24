from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import admin, briefing, kakao, subscribe


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        from app import scheduler as _scheduler  # noqa: F401
        _scheduler.start()
    except Exception:
        pass  # scheduler module not yet present — app still starts

    yield

    try:
        from app import scheduler as _scheduler  # noqa: F401
        _scheduler.shutdown()
    except Exception:
        pass


app = FastAPI(
    title="dongne.me API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dongne.me", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(subscribe.router, prefix="/api")
app.include_router(briefing.router, prefix="/api")
app.include_router(kakao.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}

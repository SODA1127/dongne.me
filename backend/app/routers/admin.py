from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException

from app.config import settings

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/trigger")
async def trigger_pipeline(x_admin_secret: str = Header(...)):
    """수동으로 브리핑 수집 파이프라인 실행. X-Admin-Secret 헤더 필요."""
    if x_admin_secret != settings.admin_secret:
        raise HTTPException(status_code=403, detail="Invalid admin secret")

    from app.pipeline import run_pipeline

    result = await run_pipeline()
    return {"status": "ok", "result": result}

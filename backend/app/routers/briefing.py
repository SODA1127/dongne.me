from __future__ import annotations

from datetime import date

from fastapi import APIRouter

router = APIRouter(prefix="/briefing", tags=["briefing"])


@router.get("/{region}/latest")
async def get_latest_briefing(region: str):
    """지역의 최신 브리핑 조회 (Supabase에서)."""
    try:
        from app.database import get_client

        client = get_client()
        result = (
            client.table("briefings")
            .select("*")
            .eq("region", region)
            .order("date", desc=True)
            .limit(3)  # weather/news/license 3개
            .execute()
        )
        return {"region": region, "briefings": result.data}
    except Exception as e:
        # DB 없을 때 graceful fallback
        return {"region": region, "briefings": [], "error": str(e)}


@router.get("/{region}/{briefing_date}")
async def get_briefing_by_date(region: str, briefing_date: date):
    """특정 날짜 브리핑 조회."""
    try:
        from app.database import get_client

        client = get_client()
        result = (
            client.table("briefings")
            .select("*")
            .eq("region", region)
            .eq("date", str(briefing_date))
            .execute()
        )
        return {"region": region, "date": str(briefing_date), "briefings": result.data}
    except Exception as e:
        return {"region": region, "date": str(briefing_date), "briefings": [], "error": str(e)}

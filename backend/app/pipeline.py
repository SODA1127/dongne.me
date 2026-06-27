"""수집 → Supabase upsert 파이프라인 오케스트레이터."""
from __future__ import annotations

import asyncio
import logging
from datetime import date

logger = logging.getLogger(__name__)


def save_briefing(region: str, briefing_date: date, category: str, data: dict) -> None:
    """Supabase briefings 테이블에 upsert."""
    from app.database import get_client

    client = get_client()
    client.table("briefings").upsert(
        {
            "region": region,
            "date": str(briefing_date),
            "category": category,
            "raw_data": data.get("raw_data"),
            "sources": data.get("sources"),
        },
        on_conflict="region,date,category",
    ).execute()


async def run_pipeline(region: str = "suwon") -> dict:
    """
    3개 카테고리(weather/news/license) 수집 후 Supabase briefings 테이블에 upsert.
    각 카테고리는 독립적으로 실행 — 하나 실패해도 나머지 계속.
    반환: {"success": [...], "failed": [...], "date": "2026-06-27"}
    """
    from app.collectors.weather import collect_weather
    from app.collectors.news import collect_news
    from app.collectors.license import collect_license

    today = date.today()

    collectors = {
        "weather": collect_weather(region),
        "news": collect_news(region),
        "license": collect_license(region),
    }

    category_names = list(collectors.keys())
    tasks = list(collectors.values())

    logger.info("파이프라인 시작: region=%s, date=%s", region, today)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    success: list[str] = []
    failed: list[dict] = []

    for category, result in zip(category_names, results):
        if isinstance(result, Exception):
            logger.error("수집 실패 [%s]: %s", category, result)
            failed.append({"category": category, "error": str(result)})
            continue

        try:
            save_briefing(region, today, category, result)
            success.append(category)
            logger.info("저장 완료 [%s]", category)
        except Exception as exc:
            logger.error("Supabase upsert 실패 [%s]: %s", category, exc)
            failed.append({"category": category, "error": f"DB 저장 실패: {exc}"})

    logger.info(
        "파이프라인 완료: success=%s, failed=%s",
        success,
        [f["category"] for f in failed],
    )

    return {
        "success": success,
        "failed": failed,
        "date": str(today),
        "region": region,
    }

import asyncio
import logging
import re

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_NAVER_NEWS_URL = "https://openapi.naver.com/v1/search/news.json"


def _strip_html(text: str) -> str:
    """HTML 태그 및 엔티티 제거."""
    text = re.sub(r"<[^>]+>", "", text)
    text = (
        text.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
    )
    return text.strip()


async def collect_news(
    region: str = "suwon",
    query: str = "수원",
    display: int = 20,
) -> dict:
    """네이버 뉴스 검색 API로 지역 뉴스 수집. 실패 시 3회 재시도."""
    last_exc: Exception | None = None

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    _NAVER_NEWS_URL,
                    headers={
                        "X-Naver-Client-Id": settings.naver_client_id,
                        "X-Naver-Client-Secret": settings.naver_client_secret,
                    },
                    params={
                        "query": query,
                        "display": display,
                        "start": 1,
                        "sort": "date",
                    },
                )

            if resp.status_code == 401:
                raise RuntimeError(
                    "네이버 API 인증 실패 — CLIENT_ID/SECRET 확인 필요"
                )

            resp.raise_for_status()
            data = resp.json()
            break

        except RuntimeError:
            raise
        except Exception as exc:
            last_exc = exc
            logger.warning("네이버 뉴스 API 시도 %d/3 실패: %s", attempt + 1, exc)
            if attempt < 2:
                await asyncio.sleep(2)
    else:
        raise RuntimeError(f"네이버 뉴스 API 수집 실패: {last_exc}")

    seen_urls: set[str] = set()
    items: list[dict] = []
    for raw in data.get("items", []):
        link = raw.get("link", "")
        if link in seen_urls:
            continue
        seen_urls.add(link)
        items.append(
            {
                "title": _strip_html(raw.get("title", "")),
                "link": link,
                "description": _strip_html(raw.get("description", "")),
                "pubDate": raw.get("pubDate", ""),
            }
        )

    return {
        "raw_data": {
            "items": items,
            "total": len(items),
            "query": query,
        },
        "sources": [
            {"title": item["title"], "url": item["link"]}
            for item in items[:5]
        ],
        "summary_hint": f"오늘 {query} 뉴스 {len(items)}건 수집됨",
    }

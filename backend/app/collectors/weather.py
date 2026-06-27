import asyncio
import logging
from datetime import datetime, timezone, timedelta

import httpx

logger = logging.getLogger(__name__)
KST = timezone(timedelta(hours=9))

_BASE_URL = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"

_PTY_MAP = {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기"}
_SKY_MAP = {"1": "맑음", "3": "구름많음", "4": "흐림"}


def _parse_items(items: list[dict], category: str, prefer_time: str = "0900") -> str:
    """카테고리 항목에서 prefer_time 기준 값 반환. 없으면 첫 번째 값."""
    matches = [i for i in items if i.get("category") == category]
    if not matches:
        return ""
    preferred = [i for i in matches if i.get("fcstTime") == prefer_time]
    target = preferred[0] if preferred else matches[0]
    return str(target.get("fcstValue", ""))


async def collect_weather(region: str = "suwon") -> dict:
    """기상청 동네예보 API에서 수원시 날씨 수집. 실패 시 3회 재시도."""
    from app.config import settings  # lazy — import safe without real key

    now_kst = datetime.now(KST)
    base_date = now_kst.strftime("%Y%m%d")
    base_time = "0500"

    params = {
        "serviceKey": settings.weather_api_key,
        "pageNo": 1,
        "numOfRows": 1000,
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": 60,
        "ny": 121,
    }

    last_exc: Exception = RuntimeError("알 수 없는 오류")
    async with httpx.AsyncClient(timeout=10.0) as client:
        for attempt in range(3):
            try:
                resp = await client.get(_BASE_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
                items: list[dict] = (
                    data["response"]["body"]["items"]["item"]
                )

                tmp = _parse_items(items, "TMP")
                pop = _parse_items(items, "POP")
                pty = _parse_items(items, "PTY")
                sky = _parse_items(items, "SKY")
                reh = _parse_items(items, "REH")

                sky_kor = _SKY_MAP.get(sky, sky)
                pty_kor = _PTY_MAP.get(pty, pty)

                if pty != "0":
                    condition = pty_kor
                else:
                    condition = sky_kor

                summary_hint = f"최고 {tmp}°C, 강수확률 {pop}%, {condition}"

                return {
                    "raw_data": {
                        "temperature": tmp,
                        "rain_prob": pop,
                        "rain_type": pty,
                        "sky": sky,
                        "humidity": reh,
                        "base_date": base_date,
                        "base_time": base_time,
                        "nx": 60,
                        "ny": 121,
                    },
                    "sources": [
                        {"title": "기상청 동네예보", "url": "https://www.weather.go.kr"}
                    ],
                    "summary_hint": summary_hint,
                }
            except Exception as exc:
                last_exc = exc
                logger.warning("기상청 API 시도 %d/3 실패: %s", attempt + 1, exc)
                if attempt < 2:
                    await asyncio.sleep(2)

    raise RuntimeError(f"기상청 API 수집 실패: {last_exc}") from last_exc

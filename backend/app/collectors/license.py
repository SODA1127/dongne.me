import logging
import asyncio
from datetime import datetime, timezone, timedelta

import httpx

from app.config import settings

logger = logging.getLogger(__name__)
KST = timezone(timedelta(hours=9))

STATUS_MAP = {
    "01": "영업/정상",
    "02": "휴업",
    "03": "폐업",
    "04": "영업정지",
    "05": "영업정지해제",
    "06": "영업취소",
    "07": "영업취소해제",
    "08": "등록취소",
}

REGION_CODE_MAP = {
    "suwon": "4111000000",
}

BASE_URL = "https://www.localdata.go.kr/platform/rest/TO0/openDataApi"


def _parse_date(date_str: str) -> datetime | None:
    """YYYYMMDD 문자열을 KST datetime으로 파싱. 빈 문자열이면 None."""
    if not date_str or not date_str.strip():
        return None
    try:
        dt = datetime.strptime(date_str.strip(), "%Y%m%d")
        return dt.replace(tzinfo=KST)
    except ValueError:
        return None


def _is_within_days(dt: datetime | None, days: int = 7) -> bool:
    if dt is None:
        return False
    cutoff = datetime.now(KST) - timedelta(days=days)
    return dt >= cutoff


async def collect_license(region: str = "suwon") -> dict:
    """localdata API에서 수원시 인허가 정보 수집. 실패 시 3회 재시도."""
    local_code = REGION_CODE_MAP.get(region, REGION_CODE_MAP["suwon"])

    params = {
        "authKey": settings.localdata_api_key,
        "opnSvcId": "07_24_04_P",
        "state": "07",
        "pageIndex": 1,
        "pageSize": 100,
        "localCode": local_code,
        "resultType": "json",
    }

    rows: list[dict] = []
    last_error: Exception | None = None

    async with httpx.AsyncClient(timeout=15.0) as client:
        for attempt in range(3):
            try:
                resp = await client.get(BASE_URL, params=params)
                resp.raise_for_status()
                data = resp.json()

                body = data.get("result", {}).get("body", {})
                rows_wrapper = body.get("rows", [])

                if rows_wrapper:
                    rows = rows_wrapper[0].get("row", [])
                else:
                    rows = []

                break  # 성공

            except Exception as exc:
                last_error = exc
                logger.warning(
                    "localdata API 시도 %d/3 실패: %s", attempt + 1, exc
                )
                if attempt < 2:
                    await asyncio.sleep(3)
        else:
            raise RuntimeError(
                f"localdata API 수집 실패: {last_error}"
            )

    new_open: list[dict] = []
    closed: list[dict] = []
    suspended: list[dict] = []

    for row in rows:
        state_code = str(row.get("trdStateGbn", "")).strip()

        if state_code == "01":
            open_date = _parse_date(row.get("apvPermYmd", ""))
            if _is_within_days(open_date):
                new_open.append(
                    {
                        "name": row.get("bplcNm", ""),
                        "category": row.get("uptaeNm", ""),
                        "address": row.get("rdnWhlAddr", ""),
                        "open_date": row.get("apvPermYmd", ""),
                    }
                )

        elif state_code == "03":
            close_date = _parse_date(row.get("dcbYmd", ""))
            if _is_within_days(close_date):
                closed.append(
                    {
                        "name": row.get("bplcNm", ""),
                        "category": row.get("uptaeNm", ""),
                        "address": row.get("rdnWhlAddr", ""),
                        "close_date": row.get("dcbYmd", ""),
                    }
                )

        elif state_code == "04":
            suspend_date = _parse_date(row.get("sttDownYmd", ""))
            if _is_within_days(suspend_date):
                suspended.append(
                    {
                        "name": row.get("bplcNm", ""),
                        "category": row.get("uptaeNm", ""),
                        "address": row.get("rdnWhlAddr", ""),
                        "suspend_date": row.get("sttDownYmd", ""),
                    }
                )

    return {
        "raw_data": {
            "new_open": new_open,
            "closed": closed,
            "suspended": suspended,
            "total_collected": len(rows),
            "region_code": local_code,
        },
        "sources": [
            {
                "title": "공공데이터포털 인허가 정보",
                "url": "https://www.localdata.go.kr",
            }
        ],
        "summary_hint": (
            f"신규오픈 {len(new_open)}건, 폐업 {len(closed)}건, "
            f"영업정지 {len(suspended)}건"
        ),
    }

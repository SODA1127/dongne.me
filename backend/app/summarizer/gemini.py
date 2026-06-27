"""Gemini 3.5 Flash 기반 카테고리별 브리핑 요약기."""
import logging
from google import genai

logger = logging.getLogger(__name__)

# 카테고리별 시스템 프롬프트
SYSTEM_PROMPTS = {
    "weather": """당신은 동네 날씨 브리핑 작성자입니다.
주어진 날씨 데이터를 바탕으로 주민이 읽기 쉬운 2-3문장 날씨 브리핑을 작성하세요.
- 기온, 강수확률, 날씨 상태를 자연스럽게 포함
- 생활 팁 한 줄 추가 (예: 우산 챙기세요, 가벼운 옷차림 추천)
- 친근하고 간결한 한국어로 작성""",

    "news": """당신은 동네 뉴스 브리핑 작성자입니다.
주어진 지역 뉴스 목록에서 주민에게 중요한 소식 3건을 선별해 요약하세요.
- 각 뉴스를 한 줄로 요약 (bullet point 형식)
- 주민 생활에 직접 영향을 주는 뉴스 우선
- 출처 링크는 포함하지 말 것 (별도 제공됨)
- 친근하고 간결한 한국어로 작성""",

    "license": """당신은 동네 가게 소식 브리핑 작성자입니다.
주어진 인허가 데이터에서 주민에게 유용한 가게 소식을 요약하세요.
- 신규 오픈 가게는 반갑게 소개
- 폐업/영업정지는 간결하게 안내
- 데이터가 없으면 "이번 주 새로운 가게 소식이 없습니다" 라고 작성
- 친근하고 간결한 한국어로 작성""",
}


def _get_client() -> genai.Client:
    """Gemini 클라이언트 생성 — API 키 우선, 없으면 ADC."""
    from app.config import settings

    if settings.gemini_api_key and not settings.gemini_api_key.startswith("placeholder"):
        return genai.Client(api_key=settings.gemini_api_key)

    # ADC fallback
    import google.auth
    from google.auth.transport.requests import Request as GRequest

    creds, _ = google.auth.default()
    if not creds.valid:
        creds.refresh(GRequest())
    return genai.Client(credentials=creds)


def _build_prompt(category: str, data: dict) -> str:
    """카테고리별 프롬프트 생성."""
    import json

    system = SYSTEM_PROMPTS.get(category, "주어진 데이터를 한국어로 간결하게 요약하세요.")
    return f"{system}\n\n데이터:\n{json.dumps(data, ensure_ascii=False, indent=2)}"


def _fallback_summary(category: str, data: dict) -> str:
    """Gemini 실패 시 원문 데이터 기반 fallback 요약."""
    if category == "weather":
        rd = data.get("raw_data", {})
        return (
            f"오늘 기온 {rd.get('temperature', '?')}°C, "
            f"강수확률 {rd.get('rain_prob', '?')}%. "
            f"날씨 정보를 불러오는 중 오류가 발생했습니다."
        )
    elif category == "news":
        items = data.get("raw_data", {}).get("items", [])
        if not items:
            return "오늘 지역 뉴스를 불러오는 중 오류가 발생했습니다."
        lines = [f"• {item['title']}" for item in items[:3]]
        return "\n".join(lines)
    elif category == "license":
        rd = data.get("raw_data", {})
        new_open = rd.get("new_open", [])
        if not new_open:
            return "이번 주 새로운 가게 소식이 없습니다."
        lines = [f"• 신규 오픈: {s['name']} ({s['category']})" for s in new_open[:3]]
        return "\n".join(lines)
    return data.get("summary_hint", "요약 정보 없음")


def summarize(category: str, data: dict) -> str:
    """
    Gemini 3.5 Flash로 카테고리별 브리핑 요약.
    실패 시 fallback 요약 반환 (예외 raise 안 함).
    """
    try:
        client = _get_client()
        prompt = _build_prompt(category, data)
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
        )
        summary = response.text.strip()
        logger.info("AI 요약 완료 [%s]: %d자", category, len(summary))
        return summary
    except Exception as exc:
        logger.warning("Gemini 요약 실패 [%s]: %s — fallback 사용", category, exc)
        return _fallback_summary(category, data)

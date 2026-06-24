# dongne.me MVP — 구현 계획

## Context

Spec: `specs/mvp-briefing/Spec.md`

핵심 제약:
- 이메일 + KakaoTalk 이중 채널 발송, 매일 오전 8시
- 수집 실패는 해당 카테고리만 스킵 — 전체 파이프라인은 계속 실행
- 친구톡 API 승인 지연 가능 → 챗봇(pull)은 API 없이 먼저 배포 가능하게 설계

## Architecture

```
monorepo/
├── backend/          FastAPI (Python) — API 서버 + 스케줄러
│   ├── app/
│   │   ├── collectors/   데이터 수집기 (weather, localdata, naver_news, naver_cafe)
│   │   ├── ai/           Gemini 요약 오케스트레이터
│   │   ├── email/        Resend 발송 + HTML 템플릿
│   │   ├── kakao/        오픈빌더 스킬 서버 + 친구톡 클라이언트
│   │   ├── routers/      FastAPI 라우터 (briefings, subscribers, kakao)
│   │   └── scheduler.py  APScheduler (수집 6시, 요약 7시, 발송 8시)
│   └── migrations/   Supabase SQL 마이그레이션
├── frontend/         Next.js (App Router, TypeScript, Tailwind)
│   └── app/
│       ├── page.tsx              랜딩
│       ├── briefings/            아카이브 목록 + 상세
│       ├── confirm/              구독 확인
│       └── unsubscribe/          구독 해지
└── .github/workflows/  CI/CD
```

**핵심 결정:**
- 수집기는 각각 독립 실행, 실패 시 빈 리스트 반환 (예외 전파 없음)
- 브리핑 상세 페이지: Next.js ISR (revalidate 3600) — 동일 날짜 반복 조회 성능
- 친구톡 발송 모듈은 API 키 없어도 인터페이스만 구현 가능하게 설계 (stub 패턴)

---

## Implementation Phases

### Phase 1: Foundation Setup

**Objective**
프로젝트 스캐폴딩, DB 스키마, 영통구 지역 상수를 확정한다. Phase 1 이후 모든 Phase가 공유하는 타입·설정·DB가 변경 없이 존재한다.

**Tasks**
- [ ] **P1-1** FastAPI 프로젝트 초기화 (pyproject.toml, `app/main.py`, `app/config.py`, Pydantic Settings) — `backend/` ← —
- [ ] **P1-2** Next.js 프로젝트 초기화 (App Router, TypeScript strict, Tailwind CSS) — `frontend/` ← —
- [ ] **P1-3** `.env` 파일 구성 + Supabase 연결 검증 (`backend/.env`, `frontend/.env.local`) — `backend/.env` ← P1-1
- [ ] **P1-4** DB 마이그레이션 SQL 작성 및 실행 (subscribers, briefings, briefing_sections, briefing_items 4개 테이블) — `backend/migrations/001_init.sql` ← P1-3
- [ ] **P1-5** 영통구 지역 상수 정의 (법정동 코드 `4111` 기준, 기상청 격자 좌표 nx=60 ny=121) — `backend/app/constants/regions.py` ← P1-1
- [ ] **P1-6** Docker Compose 설정 (backend + frontend 개발 환경) — `docker-compose.yml` ← P1-1, P1-2

### Phase 2: 데이터 수집 파이프라인

**Objective**
4개 소스(기상청, localdata, 네이버 뉴스, 네이버 카페)에서 영통구 데이터를 수집하고 DB에 원본 저장한다. Phase 2 이후 AI 요약은 항상 DB의 raw_items를 input으로 사용한다.

**Tasks**
- [ ] **P2-1** 기상청 동네예보 API 클라이언트 (격자 좌표 기반, 기온·강수·미세먼지 파싱) — `backend/app/collectors/weather.py` ← P1-5
- [ ] **P2-2** localdata.go.kr 인허가 API 클라이언트 (법정동 코드 필터, 음식점·의료기관 신규/폐업) — `backend/app/collectors/localdata.py` ← P1-5
- [ ] **P2-3** 네이버 뉴스 검색 API 클라이언트 (키워드: "영통구" / "영통" / "수원 영통", 최근 24시간) — `backend/app/collectors/naver_news.py` ← P1-3
- [ ] **P2-4** 네이버 카페 수집기 (비공식 엔드포인트, 공개 게시판, 수집 간격 ≥1초) — `backend/app/collectors/naver_cafe.py` ← P1-3
- [ ] **P2-5** og:image 썸네일 URL 추출 유틸리티 (httpx + BeautifulSoup, 실패 시 None) — `backend/app/utils/thumbnail.py` ← —
- [ ] **P2-6** 수집 파이프라인 오케스트레이터 (4개 수집기 병렬 실행, 각 실패는 빈 리스트 반환, 중복 URL 제거) — `backend/app/collectors/pipeline.py` ← P2-1, P2-2, P2-3, P2-4, P2-5
- [ ] **P2-7** APScheduler 기본 설정 + 수집 작업 등록 (매일 오전 6:00 KST) — `backend/app/scheduler.py` ← P2-6

### Phase 3: AI 요약 생성

**Objective**
수집된 raw_items를 Gemini API로 카테고리별 요약하고 briefing_sections + briefing_items에 저장한다. Phase 3 이후 이메일·KakaoTalk 발송 모듈은 DB만 읽으면 된다.

**Tasks**
- [ ] **P3-1** Gemini API 클라이언트 래퍼 (gemini-1.5-flash, JSON 출력 강제, 재시도 2회) — `backend/app/ai/gemini.py` ← P1-3
- [ ] **P3-2** 카테고리별 요약 프롬프트 (weather / local_info / news_community 각각 별도 프롬프트) — `backend/app/ai/prompts.py` ← P3-1
- [ ] **P3-3** 요약 오케스트레이터 (pipeline 결과 → 카테고리별 Gemini 요약 → briefing_sections/briefing_items DB 저장) — `backend/app/ai/summarizer.py` ← P3-2, P2-6, P1-4
- [ ] **P3-4** APScheduler에 요약 작업 추가 (매일 오전 7:00 KST, 수집 완료 후) — `backend/app/scheduler.py` ← P3-3, P2-7

### Phase 4: 이메일 발송

**Objective**
이메일 구독 신청/해지 플로우가 완성되고, 매일 오전 8시에 활성 구독자에게 브리핑 이메일이 발송된다.

**Tasks**
- [ ] **P4-1** Resend API 클라이언트 (발송, 3회 재시도, 개별 실패 스킵) — `backend/app/email/resend_client.py` ← P1-3
- [ ] **P4-2** 이메일 HTML 템플릿 (Jinja2, 날씨·생활정보·뉴스 3섹션, 썸네일 카드, 해지 링크) — `backend/app/email/templates/briefing.html` ← P4-1
- [ ] **P4-3** 구독자 라우터 (POST /subscribe, GET /confirm/{token}, GET /unsubscribe/{token}) — `backend/app/routers/subscribers.py` ← P1-4, P4-1
- [ ] **P4-4** double opt-in 확인 이메일 발송 (구독 신청 시 confirm_token 생성 → Resend 발송) — `backend/app/email/sender.py` ← P4-1, P4-2, P4-3
- [ ] **P4-5** 일일 이메일 브리핑 발송 스케줄 작업 (매일 오전 8:00 KST, 활성 구독자 전체) — `backend/app/scheduler.py` ← P4-1, P4-2, P3-3

### Phase 5: KakaoTalk 챗봇 + 친구톡

**Objective**
카카오 채널 친구 추가 시 구독 활성화, 챗봇 명령어 3종, 친구톡 자동 발송이 동작한다. 친구톡 API 키 없이도 챗봇은 독립 배포 가능.

**Tasks**
- [ ] **P5-1** 카카오 스킬 서버 라우터 (POST /kakao/skill — 오픈빌더 요청 파싱 + 응답 포맷) — `backend/app/routers/kakao.py` ← P1-4
- [ ] **P5-2** 친구 추가/차단 webhook (POST /kakao/webhook/friend — 추가 시 subscribers INSERT, 차단 시 is_active=false) — `backend/app/routers/kakao.py` ← P5-1
- [ ] **P5-3** 챗봇 명령어 핸들러 ("오늘 브리핑" / "구독 해지" / "도움말" / 폴백 — 각 응답 포맷 정의) — `backend/app/kakao/handlers.py` ← P5-1, P1-4
- [ ] **P5-4** 친구톡 발송 클라이언트 (카카오 비즈니스 API, API 키 없으면 로그만 출력하는 stub 모드) — `backend/app/kakao/friendtalk.py` ← P1-3
- [ ] **P5-5** 일일 친구톡 발송 스케줄 작업 (매일 오전 8:00 KST, 이메일 발송과 병렬, KakaoTalk 채널 활성 구독자) — `backend/app/scheduler.py` ← P5-4, P3-3

### Phase 6: Next.js 프론트엔드

**Objective**
랜딩·아카이브·상세·구독확인·해지 5개 페이지가 배포 가능한 상태이며, 실제 DB 데이터를 렌더링한다.

**Tasks**
- [ ] **P6-1** 공통 레이아웃 (Header, Footer, 글로벌 Tailwind 스타일) — `frontend/app/layout.tsx` ← P1-2
- [ ] **P6-2** 백엔드 브리핑 조회 API (GET /api/briefings?neighborhood=, GET /api/briefings/{neighborhood}/{date}) — `backend/app/routers/briefings.py` ← P1-4
- [ ] **P6-3** 랜딩 페이지 (이메일 구독 폼 + 최신 브리핑 미리보기 카드 3~5개, 썸네일+한 줄 요약) — `frontend/app/page.tsx` ← P6-1, P6-2
- [ ] **P6-4** 아카이브 목록 페이지 (동네 선택 드롭다운 + 날짜별 브리핑 카드, 빈 동네 처리) — `frontend/app/briefings/page.tsx` ← P6-1, P6-2
- [ ] **P6-5** 브리핑 상세 페이지 (ISR revalidate=3600, 카테고리별 섹션, 8시 이전 미생성 처리) — `frontend/app/briefings/[neighborhood]/[date]/page.tsx` ← P6-4
- [ ] **P6-6** 구독 확인 페이지 + 해지 페이지 (백엔드 API 호출 후 완료 안내) — `frontend/app/confirm/page.tsx`, `frontend/app/unsubscribe/page.tsx` ← P6-1, P4-3

### Phase 7: 배포 및 E2E 검증

**Objective**
DigitalOcean에 배포 완료, 전체 파이프라인(수집→요약→이메일/KakaoTalk 발송)이 실제 환경에서 24시간 정상 동작한다.

**Tasks**
- [ ] **P7-1** GitHub Actions CI/CD (backend Docker 빌드 + frontend Vercel 배포) — `.github/workflows/deploy.yml` ← P1-6
- [ ] **P7-2** DigitalOcean App Platform 설정 (backend 컨테이너 + 환경 변수) — `deploy/app.yaml` ← P7-1
- [ ] **P7-3** 이메일 E2E 검증 (테스트 주소로 전체 플로우: 신청 → 확인 → 브리핑 수신 → 해지) — — ← P4-5, P6-6
- [ ] **P7-4** KakaoTalk E2E 검증 (테스트 채널 친구 추가 → 웰컴 메시지 → 명령어 응답 → 친구톡 수신) — — ← P5-5
- [ ] **P7-5** 스케줄러 48시간 안정성 검증 (수집→요약→발송 전체 파이프라인, 실패 격리 확인) — — ← P7-3, P7-4

---

## Dependency Graph

```
P1-1 ──► P1-3 ──► P1-4 ──► P4-3 ──► P4-4 ──► P4-5 ──► P7-3
  │         │        │                              │
  │         │        └──► P3-3 ──────────────────► P5-5 ──► P7-4
  │         │                  ▲                    │
  │         ├──► P2-3 ──► P2-6 ──► P2-7 ──► P3-4  │
  │         ├──► P2-4 ──┘    │                     │
  │         └──► P3-1 ──► P3-2                     │
  │                                                 │
P1-2 ──► P6-1 ──► P6-3 ──► P7-1 ──► P7-2 ─────────┘
P1-5 ──► P2-1 ──┐
         P2-2 ──┘
```

---

## Verification Method

1. **이메일 전체 플로우**: 테스트 이메일로 구독 신청 → 확인 이메일 수신 → 링크 클릭 → 다음 날 오전 8시 브리핑 수신 → 해지 링크로 해지
2. **KakaoTalk 전체 플로우**: 테스트용 카카오 계정으로 채널 친구 추가 → 웰컴 메시지 확인 → "오늘 브리핑" 명령 → 응답 확인 → "구독 해지" → 비활성화 확인
3. **수집 파이프라인**: 스케줄러 수동 트리거 → DB에 raw_items 저장 여부 + 각 수집기 독립 실패 시 나머지 정상 수집 확인
4. **AI 요약**: summarizer 수동 실행 → briefing_sections/briefing_items 행 생성 + 요약 내용 수동 정확도 검수
5. **빈 상태/에러 처리**: 8시 이전 오늘 브리핑 URL 접근 → 안내 문구 확인 / 존재하지 않는 동네 선택 → 안내 문구 확인

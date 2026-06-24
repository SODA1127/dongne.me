# dongne.me MVP Implementation Plan

## Context

- Spec: `specs/dongne-mvp/Spec.md`
- 목표: 수원시 단일 지역 AI 브리핑 서비스 MVP — 해커톤 1-Day 완성 후 실서비스 배포
- 팀: 이기정(백엔드·AI·인프라), 김현우(프론트엔드)
- 핵심 제약: 해커톤 당일 첫 브리핑 발송 성공이 최우선

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        dongne.me                            │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Next.js     │    │  FastAPI     │    │  Supabase    │  │
│  │  (Frontend)  │◄──►│  (Backend)   │◄──►│  (PostgreSQL)│  │
│  │  Port 3000   │    │  Port 8000   │    │              │  │
│  └──────────────┘    └──────┬───────┘    └──────────────┘  │
│                             │                               │
│                    ┌────────▼────────┐                      │
│                    │  APScheduler    │                      │
│                    │  (Cron Jobs)    │                      │
│                    └────────┬────────┘                      │
│                             │                               │
│              ┌──────────────┼──────────────┐               │
│              ▼              ▼              ▼               │
│        ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│        │ 기상청   │  │ 네이버   │  │ localdata│           │
│        │ API      │  │ 뉴스 API │  │ API      │           │
│        └──────────┘  └──────────┘  └──────────┘           │
│                             │                               │
│                    ┌────────▼────────┐                      │
│                    │  Gemini API     │                      │
│                    │  (AI 요약)      │                      │
│                    └────────┬────────┘                      │
│                             │                               │
│              ┌──────────────┼──────────────┐               │
│              ▼              ▼              ▼               │
│        ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│        │  Resend  │  │  Kakao   │  │  Admin   │           │
│        │  Email   │  │  Chatbot │  │  Webhook │           │
│        └──────────┘  └──────────┘  └──────────┘           │
└─────────────────────────────────────────────────────────────┘

배포: Docker Compose → DigitalOcean App Platform
CI/CD: GitHub Actions (main push → auto deploy)
```

### 핵심 설계 결정

1. **모노레포 구조**: `backend/` + `frontend/` 디렉토리, 루트에 `docker-compose.yml`
2. **백엔드 우선**: 데이터 파이프라인 → 발송 시스템 → 프론트엔드 순서로 구축
3. **Supabase 직접 연결**: 프론트엔드에서 Supabase JS Client로 브리핑 조회 (백엔드 bypass)
4. **환경변수 중앙화**: `.env` 파일 하나로 모든 API 키 관리
5. **APScheduler in-process**: 별도 Celery/Redis 없이 FastAPI 내부에서 스케줄러 실행 (MVP 단순화)

---

## 프로젝트 구조

```
dongne.me/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 앱 진입점 + 스케줄러 시작
│   │   ├── config.py            # 환경변수 설정 (pydantic-settings)
│   │   ├── database.py          # Supabase 클라이언트
│   │   ├── scheduler.py         # APScheduler 설정 + 작업 등록
│   │   ├── collectors/
│   │   │   ├── __init__.py
│   │   │   ├── weather.py       # 기상청 API 수집
│   │   │   ├── news.py          # 네이버 뉴스 API 수집
│   │   │   └── license.py       # localdata 인허가 API 수집
│   │   ├── summarizer/
│   │   │   ├── __init__.py
│   │   │   └── gemini.py        # Gemini API 요약
│   │   ├── senders/
│   │   │   ├── __init__.py
│   │   │   ├── email.py         # Resend 이메일 발송
│   │   │   └── kakao.py         # 카카오 챗봇 웹훅 처리
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── subscribe.py     # 구독 관련 API
│   │   │   ├── briefing.py      # 브리핑 조회 API
│   │   │   ├── kakao.py         # 카카오 웹훅 API
│   │   │   └── admin.py         # 관리자 트리거 API
│   │   ├── templates/
│   │   │   └── email.html       # 이메일 HTML 템플릿 (Jinja2)
│   │   └── pipeline.py          # 전체 파이프라인 오케스트레이터
│   ├── tests/
│   │   ├── test_collectors.py
│   │   ├── test_summarizer.py
│   │   └── test_senders.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx                    # 메인 랜딩 (/)
│   │   │   ├── briefing/
│   │   │   │   └── [region]/
│   │   │   │       └── [date]/
│   │   │   │           └── page.tsx        # 브리핑 상세
│   │   │   ├── subscribe/
│   │   │   │   └── confirm/
│   │   │   │       └── page.tsx            # 구독 확인
│   │   │   └── unsubscribe/
│   │   │       └── page.tsx                # 구독 해지
│   │   ├── components/
│   │   │   ├── SubscribeForm.tsx           # 이메일 구독 폼
│   │   │   ├── RegionFilter.tsx            # 경기도 시/군/구 드롭다운
│   │   │   ├── BriefingCard.tsx            # 브리핑 카드 컴포넌트
│   │   │   ├── WeatherSection.tsx          # 날씨 섹션
│   │   │   ├── NewsSection.tsx             # 뉴스 섹션
│   │   │   └── LicenseSection.tsx          # 인허가 섹션
│   │   └── lib/
│   │       ├── supabase.ts                 # Supabase 클라이언트
│   │       └── regions.ts                  # 경기도 시/군/구 데이터
│   ├── Dockerfile
│   ├── package.json
│   └── .env.example
├── docker-compose.yml
├── docker-compose.prod.yml
├── .github/
│   └── workflows/
│       └── deploy.yml                      # GitHub Actions CI/CD
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql          # DB 스키마
└── README.md
```

---

## Implementation Phases

### Phase 0: 프로젝트 기반 셋업

**Objective**
모노레포 구조, 환경변수, Supabase 스키마, Docker 기반이 완성되어 팀원 모두 로컬에서 실행 가능한 상태.

**Tasks**
- [ ] **P0-1** 모노레포 디렉토리 구조 생성 + `.gitignore` + `README.md` — `./` ← —
- [ ] **P0-2** Supabase 프로젝트 생성 + `001_initial_schema.sql` 마이그레이션 작성 (subscribers, briefings, send_logs) — `supabase/migrations/001_initial_schema.sql` ← —
- [ ] **P0-3** FastAPI 프로젝트 초기화: `requirements.txt`, `config.py`(pydantic-settings), `database.py`(supabase-py), `main.py` 기본 구조 — `backend/` ← P0-1
- [ ] **P0-4** Next.js 프로젝트 초기화: `create-next-app` + Tailwind CSS + shadcn/ui + Supabase JS Client — `frontend/` ← P0-1
- [ ] **P0-5** `.env.example` 작성 (모든 필요 환경변수 목록화) — `backend/.env.example`, `frontend/.env.example` ← P0-3, P0-4
- [ ] **P0-6** `docker-compose.yml` 작성 (backend + frontend 서비스) — `docker-compose.yml` ← P0-3, P0-4

---

### Phase 1: 데이터 수집 파이프라인

**Objective**
기상청·네이버뉴스·인허가 3개 API에서 수원시 데이터를 수집해 Supabase `briefings` 테이블에 저장하는 파이프라인이 동작한다.

**Tasks**
- [ ] **P1-1** 기상청 동네예보 API 수집기 구현 — `backend/app/collectors/weather.py` ← P0-3
  - 수원시 격자(nx=60, ny=121) 기준 오늘 날씨 조회
  - TMP(기온), POP(강수확률), PTY(강수형태), PM10(미세먼지) 파싱
  - 실패 시 재시도 3회 + 예외 처리
- [ ] **P1-2** 네이버 뉴스 검색 API 수집기 구현 — `backend/app/collectors/news.py` ← P0-3
  - "수원" 키워드 뉴스 최신 20건 수집
  - 제목·링크·발행일·요약 파싱
  - 중복 URL 필터링
- [ ] **P1-3** localdata 인허가 API 수집기 구현 — `backend/app/collectors/license.py` ← P0-3
  - 수원시(4111000000) 최근 7일 신규 인허가 조회
  - 업태구분명·사업장명·도로명주소·영업상태 파싱
  - 신규오픈/폐업/영업정지 분류
- [ ] **P1-4** Supabase `briefings` 테이블 upsert 로직 구현 — `backend/app/database.py` ← P0-2, P0-3
  - UNIQUE(region, date, category) 기준 upsert
  - raw_data(jsonb) + sources(jsonb) 저장
- [ ] **P1-5** 수집 파이프라인 통합 테스트 — `backend/tests/test_collectors.py` ← P1-1, P1-2, P1-3, P1-4
  - 각 수집기 mock 테스트
  - Supabase 저장 검증

---

### Phase 2: AI 요약 파이프라인

**Objective**
수집된 원시 데이터를 Gemini API로 카테고리별 한국어 요약으로 변환해 `briefings.summary` 필드에 저장한다.

**Tasks**
- [ ] **P2-1** Gemini API 요약기 구현 — `backend/app/summarizer/gemini.py` ← P1-4
  - `gemini-1.5-flash` 모델 사용
  - 카테고리별 시스템 프롬프트 설계 (날씨/뉴스/인허가)
  - 응답 파싱 + fallback 처리 (API 오류 시 원문 상위 3건 반환)
  - 출처 링크 보존 로직
- [ ] **P2-2** 전체 파이프라인 오케스트레이터 구현 — `backend/app/pipeline.py` ← P1-4, P2-1
  - 수집 → 요약 → 저장 순서 실행
  - 단계별 오류 격리 (한 카테고리 실패해도 나머지 계속)
  - 실행 로그 출력
- [ ] **P2-3** APScheduler 설정 — `backend/app/scheduler.py` ← P2-2
  - 매일 07:00 KST 파이프라인 실행 등록
  - misfire_grace_time=3600 설정
  - FastAPI lifespan에 스케줄러 시작/종료 연결
- [ ] **P2-4** AI 요약 품질 검증 — `backend/tests/test_summarizer.py` ← P2-1
  - 실제 API 호출 통합 테스트 (1회)
  - fallback 동작 단위 테스트

---

### Phase 3: 구독 관리 + 이메일 발송

**Objective**
이메일 구독 신청 → double opt-in → 매일 오전 8시 브리핑 이메일 발송 → 해지 플로우가 end-to-end로 동작한다.

**Tasks**
- [ ] **P3-1** 구독 관리 API 구현 — `backend/app/routers/subscribe.py` ← P0-2, P0-3
  - `POST /api/subscribe`: 이메일 저장 + 토큰 생성 + opt-in 이메일 발송
  - `GET /api/subscribe/confirm?token=`: 상태 active 전환
  - `GET /api/unsubscribe?token=`: 상태 unsubscribed 전환
  - 중복 구독 처리 (EDGE-5)
  - 만료 토큰 처리 (EDGE-6, 24시간)
- [ ] **P3-2** 이메일 HTML 템플릿 작성 — `backend/app/templates/email.html` ← —
  - Jinja2 템플릿 (날씨·뉴스·인허가 섹션)
  - 반응형 HTML 이메일 (모바일 최적화)
  - 구독 해지 링크 포함
  - plain text fallback
- [ ] **P3-3** Resend 이메일 발송기 구현 — `backend/app/senders/email.py` ← P3-1, P3-2
  - opt-in 확인 이메일 발송
  - 일일 브리핑 이메일 발송 (활성 구독자 전체)
  - 발송 결과 `send_logs` 테이블 기록
  - 실패 시 재시도 3회 (5분 간격)
- [ ] **P3-4** 이메일 발송 스케줄 등록 — `backend/app/scheduler.py` ← P3-3, P2-3
  - 매일 08:00 KST 이메일 발송 작업 추가
- [ ] **P3-5** 발송 파이프라인 통합 테스트 — `backend/tests/test_senders.py` ← P3-3
  - Resend mock 테스트
  - 발송 로그 저장 검증

---

### Phase 4: 카카오 챗봇

**Objective**
카카오 i 오픈빌더 챗봇이 "오늘 브리핑", "구독 해지", "도움말" 명령어에 응답한다.

**Tasks**
- [ ] **P4-1** 카카오 챗봇 웹훅 API 구현 — `backend/app/routers/kakao.py` ← P2-2
  - `POST /api/kakao/webhook` 엔드포인트
  - 카카오 i 오픈빌더 스킬 서버 응답 포맷 준수
  - "오늘 브리핑": 최신 브리핑 요약 + 웹 링크 반환
  - "구독 해지": 해지 확인 버튼 카드 반환
  - "도움말": 명령어 안내 반환
  - 알 수 없는 명령어: EDGE-8 처리
- [ ] **P4-2** 카카오 i 오픈빌더 설정 가이드 작성 — `docs/kakao-setup.md` ← P4-1
  - 스킬 서버 URL 등록 방법
  - 시나리오 블록 설정 방법
  - 테스트 방법

---

### Phase 5: 웹 프론트엔드

**Objective**
경기도 시/군/구 필터 대시보드가 라이브로 접근 가능하고, 이메일 구독 신청이 웹에서 가능하다.

**Tasks**
- [ ] **P5-1** 경기도 시/군/구 데이터 + Supabase 클라이언트 설정 — `frontend/src/lib/` ← P0-4
  - 경기도 31개 시/군 데이터 (코드·이름) 정의
  - Supabase JS Client 초기화
- [ ] **P5-2** 공통 컴포넌트 구현 — `frontend/src/components/` ← P5-1
  - `RegionFilter.tsx`: 경기도 시/군/구 드롭다운 (shadcn Select)
  - `BriefingCard.tsx`: 브리핑 카드 (날짜·지역·카테고리 배지)
  - `SubscribeForm.tsx`: 이메일 입력 + 구독 버튼 (react-hook-form + zod)
- [ ] **P5-3** 날씨·뉴스·인허가 섹션 컴포넌트 구현 — `frontend/src/components/` ← P5-1
  - `WeatherSection.tsx`: 기온·강수·미세먼지 카드 UI
  - `NewsSection.tsx`: 뉴스 리스트 (제목·요약·링크)
  - `LicenseSection.tsx`: 신규오픈·폐업·영업정지 리스트
- [ ] **P5-4** 메인 랜딩 페이지 구현 — `frontend/src/app/page.tsx` ← P5-2, P5-3
  - SSR로 수원시 최신 브리핑 데이터 fetch
  - 히어로 섹션 + 구독 폼 + 브리핑 미리보기
  - 지역 필터 드롭다운 (선택 시 해당 지역 브리핑으로 이동)
  - OG 메타태그 설정
- [ ] **P5-5** 브리핑 상세 페이지 구현 — `frontend/src/app/briefing/[region]/[date]/page.tsx` ← P5-3
  - SSR로 특정 날짜·지역 브리핑 fetch
  - 날씨·뉴스·인허가 섹션 렌더링
  - 이전/다음 날짜 네비게이션
  - 구독 CTA 배너
- [ ] **P5-6** 구독 확인·해지 페이지 구현 — `frontend/src/app/subscribe/`, `frontend/src/app/unsubscribe/` ← P5-1
  - 구독 확인 페이지 (opt-in 완료 메시지)
  - 구독 해지 페이지 (해지 완료 메시지 + 재구독 CTA)

---

### Phase 6: 배포 인프라

**Objective**
GitHub Actions로 main 브랜치 push 시 DigitalOcean App Platform에 자동 배포되고, 실제 도메인(dongne.me)으로 접근 가능하다.

**Tasks**
- [ ] **P6-1** 백엔드 Dockerfile 작성 — `backend/Dockerfile` ← P0-3
  - Python 3.11-slim 베이스
  - 멀티스테이지 빌드 (의존성 캐시 최적화)
  - 비루트 사용자 실행
- [ ] **P6-2** 프론트엔드 Dockerfile 작성 — `frontend/Dockerfile` ← P0-4
  - Node 20-alpine 베이스
  - 멀티스테이지 빌드 (build → runner)
  - standalone 출력 모드
- [ ] **P6-3** `docker-compose.prod.yml` 작성 — `docker-compose.prod.yml` ← P6-1, P6-2
  - 프로덕션 환경변수 주입 방식
  - 헬스체크 설정
- [ ] **P6-4** GitHub Actions CI/CD 워크플로우 작성 — `.github/workflows/deploy.yml` ← P6-1, P6-2
  - main 브랜치 push 트리거
  - Docker 이미지 빌드 + DigitalOcean Container Registry push
  - DigitalOcean App Platform 배포 트리거
  - 배포 성공/실패 Slack 알림 (선택)
- [ ] **P6-5** DigitalOcean App Platform 설정 + 도메인 연결 — (수동 작업 가이드) ← P6-4
  - App 생성 + 환경변수 설정
  - `dongne.me` 도메인 DNS 연결
  - SSL 인증서 자동 발급 확인

---

### Phase 7: 통합 검증 + 해커톤 데모

**Objective**
수원시 브리핑이 실제로 생성되고, 팀원 이메일로 발송 성공. 웹 대시보드 라이브 접근 가능.

**Tasks**
- [ ] **P7-1** 수동 파이프라인 실행 + 브리핑 생성 검증 — `POST /api/admin/trigger` ← Phase 1~4 완료
  - 수원시 오늘 날씨·뉴스·인허가 수집 확인
  - Gemini 요약 결과 품질 검수
  - Supabase `briefings` 테이블 데이터 확인
- [ ] **P7-2** 팀원 이메일 구독 + 발송 테스트 — (수동 테스트) ← P3-3, P7-1
  - 구독 신청 → opt-in 이메일 수신 → 확인 링크 클릭
  - 수동 발송 트리거 → 브리핑 이메일 수신 확인
  - 이메일 렌더링 검수 (모바일·데스크톱)
- [ ] **P7-3** 카카오 챗봇 동작 테스트 — (수동 테스트) ← P4-1
  - "오늘 브리핑" 명령어 응답 확인
  - "도움말" 명령어 응답 확인
- [ ] **P7-4** 웹 대시보드 E2E 검증 — (수동 테스트) ← Phase 5 완료
  - 메인 페이지 로딩 + 브리핑 표시 확인
  - 지역 필터 동작 확인
  - 구독 폼 동작 확인
  - 모바일 반응형 확인
- [ ] **P7-5** 성능 + 안정성 체크 — (자동화 도구) ← P7-4
  - Lighthouse 점수 확인 (LCP < 2.5s 목표)
  - 스케줄러 07:00/08:00 KST 실행 로그 확인

---

## Dependency Graph

```
P0-1 ──┬──► P0-3 ──┬──► P1-1 ──┐
       │           ├──► P1-2 ──┤
       │           ├──► P1-3 ──┤
       │           └──► P3-1 ──┤
       │                        ▼
P0-2 ──┼──────────────────► P1-4 ──► P2-1 ──► P2-2 ──► P2-3
       │                                                  │
       └──► P0-4 ──► P5-1 ──► P5-2 ──► P5-4             │
                          └──► P5-3 ──► P5-5             │
                                                          ▼
P3-2 ──────────────────────────────────────────► P3-3 ──► P3-4
                                                  │
                                                  ▼
P6-1 ──► P6-3 ──► P6-4 ──► P6-5              P7-1 ──► P7-2
P6-2 ──►                                      P7-3
                                              P7-4 ──► P7-5
```

---

## 해커톤 1-Day 실행 순서

> 팀 분업: 이기정(백엔드) + 김현우(프론트엔드) 병렬 진행

| 시간 | 이기정 (백엔드) | 김현우 (프론트엔드) |
|------|----------------|-------------------|
| 09:00 | P0-1, P0-2, P0-3 (프로젝트 셋업) | P0-4 (Next.js 셋업) |
| 10:00 | P1-1 (기상청 API) | P5-1 (Supabase 클라이언트 + 지역 데이터) |
| 11:00 | P1-2 (네이버 뉴스 API) | P5-2 (공통 컴포넌트) |
| 12:00 | P1-3 (인허가 API) + P1-4 (DB 저장) | P5-3 (섹션 컴포넌트) |
| 13:00 | P2-1 (Gemini 요약) + P2-2 (파이프라인) | P5-4 (메인 랜딩 페이지) |
| 14:00 | P3-1 (구독 API) + P3-3 (Resend 발송) | P5-5 (브리핑 상세 페이지) |
| 15:00 | P2-3 + P3-4 (스케줄러 등록) | P5-6 (구독/해지 페이지) |
| 16:00 | P4-1 (카카오 챗봇) | P6-2 (프론트 Dockerfile) |
| 17:00 | P6-1 (백엔드 Dockerfile) + P6-3 | P6-4 (GitHub Actions) |
| 18:00 | P6-5 (DigitalOcean 배포) | P7-4 (웹 E2E 검증) |
| 18:30 | P7-1 + P7-2 (브리핑 생성 + 이메일 발송 테스트) | |

---

## Verification Method

### 자동화 검증
```bash
# 백엔드 테스트
cd backend && pytest tests/ -v

# 프론트엔드 타입 체크
cd frontend && npx tsc --noEmit

# Docker 빌드 검증
docker-compose build

# 로컬 실행 검증
docker-compose up -d
curl http://localhost:8000/health
curl http://localhost:3000
```

### 수동 검증 체크리스트
- [ ] 수원시 날씨 데이터 수집 성공 (Supabase 확인)
- [ ] 네이버 뉴스 20건 수집 성공 (Supabase 확인)
- [ ] 인허가 데이터 수집 성공 (Supabase 확인)
- [ ] Gemini 요약 결과 품질 확인 (수동 검수)
- [ ] 이메일 구독 신청 → opt-in 이메일 수신 확인
- [ ] 브리핑 이메일 발송 성공 (팀원 수신 확인)
- [ ] 카카오 챗봇 "오늘 브리핑" 응답 확인
- [ ] 웹 대시보드 https://dongne.me 접근 가능
- [ ] 경기도 지역 필터 동작 확인
- [ ] 모바일 반응형 확인

### 성공 기준 (MVP)
| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| 일일 자동 발송 성공률 | 99%+ | send_logs 테이블 |
| 브리핑 정확도 | 90%+ | 수동 검수 |
| 웹 LCP | < 2.5s | Lighthouse |
| API 응답 시간 | < 500ms (p95) | 로컬 테스트 |

---

## 환경변수 목록

```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Google Gemini
GEMINI_API_KEY=AIza...

# Resend
RESEND_API_KEY=re_...
FROM_EMAIL=briefing@dongne.me

# 기상청 공공 API
WEATHER_API_KEY=...

# 네이버 뉴스 API
NAVER_CLIENT_ID=...
NAVER_CLIENT_SECRET=...

# 공공데이터포털 (localdata)
LOCALDATA_API_KEY=...

# 카카오
KAKAO_CHANNEL_ID=...

# 앱 설정
APP_URL=https://dongne.me
ADMIN_SECRET=...  # /api/admin/trigger 보호용
TZ=Asia/Seoul
```

# dongne.me MVP Spec

> 공공 OpenAPI + AI 요약으로 매일 아침 동네 브리핑을 자동 제공하는 하이퍼로컬 구독 서비스

## Purpose

동네 정보가 파편화되어 있어 주민들이 공사·교통·행사·뉴스를 각각 다른 채널에서 확인해야 하는 불편함을 해소한다.
공공 OpenAPI 데이터를 자동 수집하고 AI(Gemini)로 요약해 매일 오전 8시 이메일·카카오톡으로 브리핑을 발송한다.

**MVP 가설**: "AI 자동 브리핑 구독 수요가 있다" — 수원시 단일 지역으로 검증.

**팀**: 이기정(백엔드·AI), 김현우(프론트엔드)

---

## Requirements

### Functional

#### 데이터 수집 파이프라인
- REQ-1: 기상청 동네예보 API에서 수원시 기온·강수·미세먼지 데이터를 수집한다
- REQ-2: 네이버 뉴스 검색 API에서 "수원" 키워드 지역 뉴스를 수집한다 (최대 100건/회)
- REQ-3: 공공데이터포털 localdata.go.kr에서 수원시 신규 인허가(음식점·폐업·영업정지) 데이터를 수집한다
- REQ-4: 수집된 원시 데이터는 Supabase PostgreSQL에 저장한다 (중복 방지 upsert)
- REQ-5: 수집 파이프라인은 매일 오전 7시에 APScheduler로 자동 실행된다

#### AI 요약 파이프라인
- REQ-6: 수집된 데이터를 카테고리별(날씨·뉴스·인허가)로 Gemini API에 전달해 한국어 요약을 생성한다
- REQ-7: 요약 결과는 브리핑 레코드로 Supabase에 저장한다 (날짜·지역·카테고리 인덱스)
- REQ-8: AI 요약 실패 시 원문 데이터 fallback으로 브리핑을 생성한다
- REQ-9: 각 브리핑 항목에는 원문 출처 링크를 반드시 포함한다

#### 구독 관리
- REQ-10: 사용자는 이메일 주소만으로 구독 신청할 수 있다 (회원가입 불필요)
- REQ-11: 구독 신청 시 double opt-in 확인 이메일을 발송한다
- REQ-12: 구독자는 이메일 내 원클릭 링크로 구독 해지할 수 있다
- REQ-13: 구독자 정보(이메일·지역·상태·구독일)는 Supabase에 저장한다

#### 이메일 발송
- REQ-14: 매일 오전 8시 활성 구독자에게 Resend API로 HTML 이메일을 발송한다
- REQ-15: 이메일 템플릿은 날씨·뉴스·인허가 3개 섹션으로 구성된다
- REQ-16: 발송 결과(성공·실패·bounce)를 Supabase에 로깅한다

#### 카카오톡 발송
- REQ-17: 카카오 i 오픈빌더 챗봇으로 "오늘 브리핑", "구독 해지", "도움말" 명령어를 지원한다
- REQ-18: 카카오 친구톡 API 승인 전에는 챗봇(pull) 방식만 제공한다 (승인 후 push 추가)

#### 웹 대시보드
- REQ-19: 경기도 시/군/구 필터로 지역별 브리핑을 열람할 수 있는 웹 페이지를 제공한다
- REQ-20: 날짜별 브리핑 아카이브를 비로그인으로 접근할 수 있다
- REQ-21: 웹 페이지에서 이메일 구독 신청 폼을 제공한다
- REQ-22: 최신 브리핑은 SSR(Server-Side Rendering)로 제공해 SEO를 최적화한다

#### 배포 인프라
- REQ-23: 백엔드(FastAPI)와 프론트엔드(Next.js)는 Docker 컨테이너로 패키징한다
- REQ-24: GitHub Actions로 main 브랜치 push 시 DigitalOcean App Platform에 자동 배포한다

### Non-Functional

- NFR-1: 일일 자동 발송 성공률 99% 이상
- NFR-2: 브리핑 정확도 수동 검수 기준 90% 이상
- NFR-3: 웹 페이지 LCP 2.5초 이하 (Core Web Vitals)
- NFR-4: API 응답 시간 500ms 이하 (p95)
- NFR-5: 공공 API 호출 실패 시 재시도 3회 후 알림 발송
- NFR-6: 환경변수로 모든 API 키 관리 (코드에 하드코딩 금지)

---

## UI / Interaction

### 웹 페이지 (Next.js)

#### 메인 랜딩 페이지 (`/`)
- 히어로 섹션: 서비스 소개 + 이메일 구독 신청 폼
- 오늘의 브리핑 미리보기 (수원시 기본값)
- 경기도 시/군/구 드롭다운 필터
- 서비스 특징 소개 섹션

#### 브리핑 상세 페이지 (`/briefing/[region]/[date]`)
- 지역명 + 날짜 헤더
- 날씨 섹션: 기온·강수·미세먼지 카드
- 뉴스 섹션: 제목·요약·원문 링크 리스트
- 인허가 섹션: 신규 오픈·폐업·영업정지 리스트
- 이전/다음 날짜 네비게이션

#### 구독 확인 페이지 (`/subscribe/confirm`)
- double opt-in 이메일 링크 클릭 후 도달하는 페이지
- 구독 완료 메시지 + 첫 브리핑 예정 안내

#### 구독 해지 페이지 (`/unsubscribe`)
- 해지 확인 메시지
- 재구독 유도 CTA

### 이메일 템플릿

```
제목: [동네브리핑] 수원시 오늘의 동네 소식 (MM/DD)

─────────────────────────────
🌤 오늘의 날씨
  기온: 최저 N°C / 최고 N°C
  강수: N%
  미세먼지: 좋음/보통/나쁨
─────────────────────────────
📰 오늘의 지역 뉴스
  1. [제목] — 출처 링크
  2. [제목] — 출처 링크
  ...
─────────────────────────────
🏪 동네 가게 소식
  신규 오픈: [상호명] (업종)
  폐업: [상호명]
─────────────────────────────
구독 해지: [원클릭 링크]
```

### 카카오 챗봇 플로우

```
사용자: "오늘 브리핑"
봇: [오늘 날짜 브리핑 요약 텍스트 + 웹 링크]

사용자: "구독 해지"
봇: "구독을 해지하시겠습니까? [확인] [취소]"
  → 확인: "구독이 해지되었습니다."

사용자: "도움말"
봇: "사용 가능한 명령어: 오늘 브리핑 / 구독 해지 / 도움말"
```

---

## Data Contracts

### Supabase 스키마

#### `subscribers` 테이블
```sql
id          uuid PRIMARY KEY DEFAULT gen_random_uuid()
email       text UNIQUE NOT NULL
region      text NOT NULL DEFAULT 'suwon'  -- 지역 코드
status      text NOT NULL DEFAULT 'pending' -- pending | active | unsubscribed
token       text UNIQUE NOT NULL  -- double opt-in / 해지 토큰
created_at  timestamptz DEFAULT now()
confirmed_at timestamptz
```

#### `briefings` 테이블
```sql
id          uuid PRIMARY KEY DEFAULT gen_random_uuid()
region      text NOT NULL  -- 'suwon'
date        date NOT NULL
category    text NOT NULL  -- 'weather' | 'news' | 'license'
raw_data    jsonb          -- 원시 API 응답
summary     text           -- Gemini 요약 결과
sources     jsonb          -- [{title, url}]
created_at  timestamptz DEFAULT now()
UNIQUE(region, date, category)
```

#### `send_logs` 테이블
```sql
id            uuid PRIMARY KEY DEFAULT gen_random_uuid()
subscriber_id uuid REFERENCES subscribers(id)
briefing_date date NOT NULL
channel       text NOT NULL  -- 'email' | 'kakao'
status        text NOT NULL  -- 'sent' | 'failed' | 'bounced'
sent_at       timestamptz DEFAULT now()
error_message text
```

### FastAPI 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/subscribe` | 구독 신청 (email, region) |
| GET | `/api/subscribe/confirm?token=` | double opt-in 확인 |
| GET | `/api/unsubscribe?token=` | 구독 해지 |
| GET | `/api/briefing/{region}/{date}` | 브리핑 조회 |
| GET | `/api/briefing/{region}/latest` | 최신 브리핑 조회 |
| POST | `/api/kakao/webhook` | 카카오 챗봇 웹훅 |
| POST | `/api/admin/trigger` | 수동 브리핑 생성 트리거 (내부용) |

### 외부 API 연동

#### 기상청 동네예보 API
- Base URL: `https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0`
- 수원시 격자 좌표: nx=60, ny=121
- 필드: TMP(기온), POP(강수확률), PTY(강수형태), REH(습도)

#### 네이버 뉴스 검색 API
- Base URL: `https://openapi.naver.com/v1/search/news.json`
- 쿼리: `수원 {카테고리}` (날씨/교통/행사 등)
- 헤더: X-Naver-Client-Id, X-Naver-Client-Secret

#### 공공데이터포털 인허가 API
- Base URL: `https://www.localdata.go.kr/platform/rest/TO0/openDataApi`
- 수원시 코드: 4111000000
- 필드: 업태구분명, 사업장명, 도로명주소, 인허가일자, 영업상태구분코드

#### Gemini API
- Model: `gemini-1.5-flash` (비용 효율)
- 프롬프트 구조: 시스템 프롬프트(한국어·지역 맥락) + 원시 데이터 JSON

#### Resend API
- From: `briefing@dongne.me`
- 템플릿: HTML + plain text fallback

---

## Edge Cases & Error States

- EDGE-1: 기상청 API 응답 없음 → "날씨 정보를 가져올 수 없습니다" 메시지로 대체, 발송은 계속
- EDGE-2: 네이버 뉴스 API 일일 한도(25,000건) 초과 → 캐시된 전날 뉴스 사용 + 관리자 알림
- EDGE-3: Gemini API 오류/타임아웃 → 원문 데이터 상위 3건 그대로 사용 (fallback)
- EDGE-4: Resend 발송 실패 → 최대 3회 재시도 (5분 간격), 이후 send_logs에 failed 기록
- EDGE-5: 중복 구독 신청 → "이미 구독 중입니다" 응답, 재확인 이메일 발송
- EDGE-6: 만료된 opt-in 토큰 (24시간 초과) → "링크가 만료되었습니다. 재구독 신청해주세요"
- EDGE-7: 인허가 API 데이터 없음 → 해당 섹션 "이번 주 신규 소식이 없습니다"로 표시
- EDGE-8: 카카오 챗봇 알 수 없는 명령어 → "도움말을 입력하시면 사용 가능한 명령어를 안내해드립니다"
- EDGE-9: 스케줄러 실행 중 서버 재시작 → APScheduler misfire_grace_time 설정으로 재실행
- EDGE-10: 동일 날짜 브리핑 중복 생성 → UNIQUE(region, date, category) 제약으로 upsert 처리

---

## Dependencies

### 외부 서비스
- Supabase (PostgreSQL + Auth) — 무료 플랜 (500MB DB, 2GB 파일)
- Google Gemini API — `gemini-1.5-flash` 무료 티어 (15 RPM, 1M TPD)
- Resend — 무료 플랜 (3,000건/월)
- 기상청 공공 API — 무료 (일 1,000회 제한)
- 네이버 뉴스 검색 API — 무료 (일 25,000건)
- 공공데이터포털 localdata API — 무료
- 카카오 i 오픈빌더 — 무료 (친구톡은 별도 심사 필요)
- DigitalOcean App Platform — $5/월 (Basic Droplet)

### 내부 의존성
- 데이터 수집 완료 → AI 요약 실행 가능
- AI 요약 완료 → 이메일 발송 가능
- double opt-in 확인 → 이메일 발송 대상 포함

### 전제 조건
- `dongne.me` 도메인 DNS 설정 완료
- Resend에서 `dongne.me` 도메인 인증 완료
- 각 공공 API 키 발급 완료

---

## Out of Scope (MVP)

- 개인화 알림 설정 (관심 카테고리 선택)
- 지도 기반 UI (Kakao Maps)
- 소상공인 광고 판매 기능
- 트렌드 분석 대시보드
- 안전·치안, 교통·도로 카테고리 (Phase 2)
- 수원시 외 지역 확장 (Phase 2)
- 카카오 친구톡 push 발송 (API 승인 후 Phase 2)
- 프리미엄 구독 결제 (Phase 2)
- 국내 LLM 전환 (Phase 3)
- 모바일 앱

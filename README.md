# dongne.me - 동네 AI 브리핑

공공 OpenAPI + AI 요약으로 매일 아침 동네 소식을 이메일로 받아보는 서비스입니다.

## 기술 스택

| 영역 | 기술 |
|------|------|
| **백엔드** | FastAPI, Python 3.11+ |
| **프론트엔드** | Next.js 14+, TypeScript, React |
| **데이터베이스** | Supabase (PostgreSQL) |
| **AI** | Google Gemini API |
| **배포** | Docker, Docker Compose |

## 프로젝트 구조

```
dongne.me/
├── backend/                    # FastAPI 백엔드
│   ├── app/
│   │   ├── collectors/        # 공공 API 데이터 수집
│   │   ├── summarizer/        # AI 요약 로직
│   │   ├── senders/           # 이메일 발송
│   │   ├── routers/           # API 라우트
│   │   └── templates/         # 이메일 템플릿
│   └── tests/                 # 테스트
├── frontend/                   # Next.js 프론트엔드
│   └── src/
│       ├── app/
│       │   ├── briefing/      # 브리핑 페이지
│       │   ├── subscribe/     # 구독 페이지
│       │   │   └── confirm/   # 구독 확인
│       │   └── unsubscribe/   # 구독 해제
│       ├── components/        # 재사용 컴포넌트
│       └── lib/               # 유틸리티
├── supabase/
│   └── migrations/            # DB 마이그레이션
├── .github/
│   └── workflows/             # CI/CD 파이프라인
└── docs/                      # 문서

```

## 로컬 실행 방법

### 사전 요구사항
- Docker & Docker Compose
- Python 3.11+ (로컬 개발 시)
- Node.js 18+ (로컬 개발 시)

### 1. 환경 설정

```bash
# 루트 디렉토리에서
cp .env.example .env
```

`.env` 파일에 다음 정보를 입력하세요:
- `GEMINI_API_KEY`: Google Gemini API 키
- `SUPABASE_URL`: Supabase 프로젝트 URL
- `SUPABASE_KEY`: Supabase 공개 키
- `SMTP_PASSWORD`: 이메일 발송용 SMTP 비밀번호

### 2. Docker Compose로 실행

```bash
docker-compose up -d
```

- **백엔드**: http://localhost:8000
- **프론트엔드**: http://localhost:3000
- **Supabase**: http://localhost:54321

### 3. 로컬 개발 (선택사항)

**백엔드**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**프론트엔드**:
```bash
cd frontend
npm install
npm run dev
```

## 팀

- **백엔드**: 이기정
- **프론트엔드**: 김현우

## 라이선스

MIT

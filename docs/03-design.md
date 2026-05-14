# 03. Design — 기술 결정

## 결정 표 (8개)

각 결정은 **선택 / 대안 / 근거 / 트레이드오프** 형식으로 기록한다.

---

### 1) 백엔드 프레임워크

| 항목 | 내용 |
|---|---|
| **선택** | **FastAPI** |
| **대안** | Django, Express |
| **근거** | 비동기 기본, Pydantic 검증 내장, OpenAPI 자동 생성, 가벼움 — MVP CRUD에 과하지 않다. |
| **트레이드오프** | Django의 admin·ORM·인증 풀스택 패키지를 포기. 인증 등은 직접 조합해야 함. |

### 2) 프론트엔드

| 항목 | 내용 |
|---|---|
| **선택** | **Vanilla JS + Tailwind CDN** |
| **대안** | React, Vue |
| **근거** | MVP 규모에 빌드 파이프라인 불필요. 학습·디버깅 비용 0, HTML 한 파일로 동작 확인 가능. |
| **트레이드오프** | 컴포넌트 재사용·상태 관리 추상화가 없다. 화면 수가 늘면 React로 이주해야 함. |

### 3) 데이터베이스 / ORM

| 항목 | 내용 |
|---|---|
| **선택** | **SQLite (MVP) → PostgreSQL (확장)** + **SQLAlchemy** |
| **대안** | PostgreSQL 처음부터, MongoDB |
| **근거** | SQLite는 파일 하나, 설정 0. SQLAlchemy를 쓰면 Postgres 전환 시 코드 변경 최소. |
| **트레이드오프** | SQLite는 동시 쓰기 약함, 일부 타입(JSONB 등) 부재. 확장 시점에 마이그레이션 필요. |

### 4) CSS

| 항목 | 내용 |
|---|---|
| **선택** | **Tailwind만 사용** |
| **대안** | styled-components, CSS Modules, 순수 CSS |
| **근거** | 클래스 한 줄로 UI 톤 통일, 디자인 토큰을 클래스로 강제 가능. |
| **트레이드오프** | HTML 클래스가 길어진다. **styled-components 등 CSS-in-JS는 금지** — 번들 비용·일관성 훼손. |

### 5) 실시간성

| 항목 | 내용 |
|---|---|
| **선택** | **MVP: 폴링 (3초 주기)** |
| **대안** | WebSocket, SSE |
| **근거** | 10명 규모·CRUD 빈도라면 폴링으로 충분. 인프라·재연결 로직 불필요. |
| **트레이드오프** | 실시간성 떨어지고 불필요 요청 발생. **WebSocket은 확장 단계에서도 보류**, 명백한 니즈가 생긴 뒤 재검토. |

### 6) 프론트 상태 관리

| 항목 | 내용 |
|---|---|
| **선택** | **모듈 변수 + DOM 직접 갱신** |
| **대안** | Redux, Zustand, Signals |
| **근거** | Vanilla JS 선택과 일관. 화면 1개·상태 작아 추상화 불필요. |
| **트레이드오프** | 상태 ↔ DOM 동기화를 직접 관리해야 함. 화면이 늘면 곧 한계 도달. |

### 7) 디자인 시스템

| 항목 | 내용 |
|---|---|
| **선택** | **Mac OS UI 톤 (자체 토큰)** |
| **대안** | Material UI, Ant Design |
| **근거** | 외부 컴포넌트 라이브러리는 톤이 강해 Mac OS 느낌을 덮어쓴다. Tailwind 토큰으로 직접 정의가 가볍다. |
| **트레이드오프** | 컴포넌트(모달·드롭다운 등)를 직접 만들어야 함. |
| **디자인 토큰** | `rounded-xl`, `shadow-lg`, `backdrop-blur`, 시스템 폰트(`font-sans` + system stack), **터치 타깃 ≥ 44px** |

### 8) 테마 (라이트/다크)

| 항목 | 내용 |
|---|---|
| **선택** | **Tailwind `dark:` 변형 + `localStorage('theme')`** |
| **대안** | CSS 변수 수동 토글, prefers-color-scheme 전용 |
| **근거** | Tailwind 기본 메커니즘과 정합. 사용자 선택을 영속화하면서 OS 기본도 존중. |
| **트레이드오프** | `<html>`의 `class` 토글 로직을 직접 작성해야 함. |
| **초기값 규칙** | `localStorage('theme')` 값이 있으면 그 값, 없으면 `prefers-color-scheme`. |

---

### 10) 데이터 내보내기 (Export)

| 항목 | 내용 |
|---|---|
| **선택** | `GET /api/tasks/export` — JSON 파일 다운로드 (`Content-Disposition: attachment`) |
| **대안** | CSV 형식 병행, 가져오기(Import) 까지 왕복 지원 |
| **근거** | MVP 백업/이관 최소 요건만 충족. JSON 단일 포맷으로 응답 봉투(`{version, exported_at, count, tasks[]}`) 통일. CSV·import 도입은 검증·충돌·escape 비용 큼. |
| **트레이드오프** | 백업만 가능, 복원은 별도 도구 또는 향후 import API 필요. CSV로 Excel 직편집 불가. |
| **응답 봉투** | `{"version": 1, "exported_at": ISO8601, "count": N, "tasks": [TaskOut, ...]}` |

### 9) 프론트엔드 날짜 포맷팅

| 항목 | 내용 |
|---|---|
| **선택** | **dayjs** (코어) + `locale/ko` + `plugin/relativeTime` (CDN 로드) |
| **대안** | date-fns (CDN 통합 로드 무거움), Luxon (~70KB · MVP에 과함), 순수 `Date.toLocaleString` (상대 시간 미지원) |
| **근거** | 코어 ~2KB, CDN UMD 로드 가능 → Vanilla + CDN 정책(결정 #2)과 정합. 한국어 locale 내장, `fromNow()` 한 줄로 "n분 전" 표시. |
| **트레이드오프** | 타임존 다국화·달력 연산이 본격 필요해지면 Luxon으로 교체 필요. CDN 의존이라 오프라인 환경에서 동작 안 함. |

---

## 보조 의존성 (Support Dependencies)

본 문서 결정 표(1~8)에서 선택한 핵심 스택을 운영·테스트하기 위해 필요한 **표준 동반 도구**.
"돌발 의존성"이 아니라 핵심 선택의 자연스러운 동반자로 간주한다.

| 패키지 | 영역 | 도입 사유 |
|---|---|---|
| `uvicorn` | 백엔드 런타임 | FastAPI 공식 권장 ASGI 서버. FastAPI 단독으로는 실행 불가. |
| `python-dotenv` | 환경 변수 로딩 | `.env` 파일을 `os.environ`에 로드. 시크릿 하드코딩 금지 규칙 준수에 필요. |
| `pytest` | 테스트 러너 | `05-conventions.md` 에 명시된 테스트 프레임워크. |
| `httpx` | 테스트 클라이언트 | FastAPI `TestClient` 가 내부적으로 사용. API 통합 테스트의 표준. |

> 위 4개를 제외한 추가 패키지는 아래 정책을 따른다.

## 의존성 추가 정책 (절대 규칙)

> **이 문서(`03-design.md`)에 도입 사유를 적기 전에는 어떤 패키지·라이브러리·CLI도 추가하지 않는다.**

추가 절차:
1. 후보 라이브러리와 **대안 2개 이상** 비교.
2. **근거 / 트레이드오프 / 도입 시점**을 위 결정 표 형식으로 본 문서에 기재.
3. 사용자 승인 후 `requirements.txt` / `package.json` / `pyproject.toml` 등에 반영.

근거 없이 추가된 의존성은 **즉시 제거** 대상이다.

# 05. Conventions — 작업 규약

## 1. 명명 규칙 (Naming)

| 영역 | 규칙 | 예시 |
|---|---|---|
| 백엔드 (Python) | `snake_case` | `def get_task_by_id(task_id: int): ...` |
| 백엔드 모듈/파일 | `snake_case.py` | `task_service.py` |
| 프론트 (JS) 변수·함수 | `camelCase` | `function fetchTasks() { ... }` |
| 프론트 컴포넌트/클래스 | `PascalCase` | `class TaskCard { ... }` |
| DB 컬럼 | `snake_case` | `due_at`, `created_at` |
| API 경로 | `kebab-case` (필요 시) | `/api/tasks` |
| 상수 | `UPPER_SNAKE_CASE` | `MAX_TITLE_LENGTH = 200` |

### 언어
- **식별자**(변수·함수·클래스·파일명·DB 컬럼·API 경로): **영어만 사용**.
- **주석·문서**: **한국어 허용**. 의미가 명확하면 한국어 권장.

---

## 2. 금지 사항 (Hard Bans)

| # | 금지 | 이유 | 대안 |
|---|---|---|---|
| 1 | `print()` 디버깅 | 운영 로그에 노이즈, 레벨 구분 불가 | `logging` 모듈 (`logger.debug/info/warning/error`) |
| 2 | bare `except:` | 모든 예외를 삼켜 원인 추적 불가 | `except SpecificError as e:` 로 좁혀 잡기 |
| 3 | 비밀번호·키 하드코딩 | 보안 사고·유출 위험 | `.env` + `os.getenv("KEY")` |
| 4 | TypeScript `any` 타입 | 타입 시스템 무력화·의미 상실 | 명시적 타입 / `unknown` + 좁히기 |
| 5 | CSS `!important` | 우선순위 꼬임·유지보수 지옥 | 셀렉터 특이성 개선, Tailwind 클래스 순서 정리 |

> 위 5개는 **PR 자동 거절** 사유로 본다.

---

## 3. 테스트 정책

- **프레임워크**: `pytest` (백엔드).
- **커버해야 할 케이스 (최소)**:
  - **정상 케이스** — 기대 응답·상태 코드 확인.
  - **404 케이스** — 존재하지 않는 `id` 조회/수정/삭제.
  - **400 케이스** — 필수 누락·형식 위반 (`title`, `status`, `due_at`).
- 기능 추가·버그 수정 시 **테스트를 함께 작성·갱신**한다. 테스트 없는 변경은 "완료"로 보고하지 않는다 (CLAUDE.md 절대 규칙 #3).

### 테스트 파일 위치·명명
- 위치: `backend/tests/`
- 명명: `test_<대상>.py` (예: `test_tasks_api.py`)
- 함수: `test_<동작>_<조건>` (예: `test_create_task_returns_201`)

---

## 4. Git 커밋 규칙

### 형식
```
<type>: <한국어 요약 50자 이내>
```

### 타입 (type)
| 타입 | 사용 시점 |
|---|---|
| `feat` | 새로운 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서만 변경 (코드 영향 없음) |
| `refactor` | 동작 변경 없는 구조 개선 |
| `test` | 테스트 추가·수정 |
| `chore` | 빌드·설정·잡일 (의존성 업데이트 등) |

### 예시
```
feat: Task 생성 API 추가
fix: due_at ISO 8601 검증 누락 수정
docs: Phase 1 설계 문서 7종 작성
refactor: task_service 책임 분리
test: Task 단건 조회 404 케이스 추가
chore: requirements.txt 의존성 정리
```

### 브랜치
- 기본: `main` (직접 푸시 가능, MVP 한정)
- 확장 단계부터 `feat/<주제>`, `fix/<주제>` 분기 권장.

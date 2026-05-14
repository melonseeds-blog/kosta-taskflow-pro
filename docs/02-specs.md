# 02. Specs — 기능 명세

## 1. 데이터 모델 — `Task`

| 필드 | 타입 | 필수 | 기본값 | 비고 |
|---|---|---|---|---|
| `id` | INTEGER (PK, auto) | — | — | 서버 발급 |
| `title` | VARCHAR(200) | ✅ | — | 빈 문자열 불가 |
| `description` | TEXT | ❌ | `NULL` | 길이 제한 없음 (MVP) |
| `status` | ENUM(`todo`, `in_progress`, `done`) | ✅ | `todo` | 3개 값 외 거부 |
| `due_at` | DATETIME (UTC) | ❌ | `NULL` | ISO 8601, 시간까지 포함 |
| `created_at` | DATETIME (UTC) | ✅ | now() | 서버 자동 |
| `updated_at` | DATETIME (UTC) | ✅ | now() | 수정 시 자동 갱신 |

### 검증 규칙

| 위반 케이스 | HTTP 상태 |
|---|---|
| `title` 누락·빈 문자열·200자 초과 | **400** |
| `status` 값이 enum 밖 | **400** |
| `due_at` 형식이 ISO 8601 아님 | **400** |
| 존재하지 않는 `id` 조회/수정/삭제 | **404** |

> `due_at`은 **반드시 ISO 8601 (UTC, 예: `2026-05-12T18:00:00Z`)** 로 받는다.

---

## 2. REST API (5개 엔드포인트)

| # | 메서드 | 경로 | 성공 코드 | 설명 | 응답 본문 |
|---|---|---|---|---|---|
| 1 | `POST`   | `/api/tasks`      | **201** | 생성             | 생성된 Task 전체 |
| 2 | `GET`    | `/api/tasks`      | **200** | 목록             | Task 배열 (※ `description` 제외) |
| 3 | `GET`    | `/api/tasks/{id}` | **200** | 단건 조회        | Task 전체 (`description` 포함) |
| 4 | `PUT`    | `/api/tasks/{id}` | **200** | **부분 수정**    | 갱신된 Task 전체 |
| 5 | `DELETE` | `/api/tasks/{id}` | **204** | 삭제             | 없음 |

### 응답 본문 차이 — 목록 vs 단건
- **목록 (`GET /api/tasks`)**: `description` 필드 **제외** (네트워크 비용 절감)
- **단건 (`GET /api/tasks/{id}`)**: `description` **포함**

### `PUT` 동작 (부분 수정)
- 요청 본문에 포함된 필드만 갱신, 나머지는 유지.
- 예: `{ "status": "done" }` 만 보내면 `status`만 변경.

---

## 3. 화면 명세 — CRUD 4종 모두 UI에서

### 3.1 추가 (Create)
- **입력 폼**: `title` / `due_at` / `status`
- `title`만 필수, 나머지는 선택.
- 제출 시 `POST /api/tasks` 호출 → 성공하면 목록에 즉시 반영.

### 3.2 목록 (Read)
- **카드형 리스트**.
- 각 카드 구성:
  - `title`
  - **status 배지** (`todo` / `in_progress` / `done` — 색상 구분)
  - **`due_at` 표기**: `D-N HH:MM` 형식
    - 예: 마감이 3일 5시간 뒤 → `D-3 17:00`
    - 마감 지남 → `D+N` 으로 표시 (음수 표기)

### 3.3 수정 (Update)
- 카드를 **클릭 → 모달** 오픈.
- 모달에서 `title` / `description` / `status` / `due_at` 편집.
- 저장 시 `PUT /api/tasks/{id}` 호출.

### 3.4 삭제 (Delete)
- 카드 우측 **휴지통 아이콘** 클릭.
- **확인 다이얼로그** 표시 ("삭제하시겠습니까?").
- 확인 시 `DELETE /api/tasks/{id}` 호출 → 목록에서 제거.

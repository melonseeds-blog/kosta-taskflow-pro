# 04. Tasks — 작업 계획

## 진행 규칙 (Process Rule)
1. **순서대로만** 진행한다. Phase 건너뛰기 금지.
2. **병렬 금지**. 한 번에 하나의 단계만 진행한다.
3. **단계별 검증 필수**. 표의 "검증 방법" 통과 전 다음 단계로 가지 않는다.
4. **확장 단계(JWT/팀/Kanban/채팅/CI·CD)는 본 문서에 포함하지 않는다.** MVP 완료 후 별도 문서에서 다룬다.

---

## Phase 1 — 설계 (10단계) ✅ 완료
> 목표: `CLAUDE.md` + `docs/` 6종을 모두 갖추고 Git 저장소를 초기화한다.
> 검증: 10/10 단계 통과 — 커밋 `eec91a7` (문서 7종), `4d64b2d` (.gitignore + 보조 의존성).

| # | 작업 | 검증 방법 |
|---|---|---|
| 1 | `CLAUDE.md` 작성 | 파일 존재 + 절대 규칙 5개 항목이 모두 보임 |
| 2 | `docs/00-overview.md` 작성 | 6개 파일 매핑표가 6행으로 채워져 있음 |
| 3 | `docs/01-product.md` 작성 | MVP 성공 기준 5개가 명시되어 있음 |
| 4 | `docs/02-specs.md` 작성 | Task 모델 7필드 + REST API 5개 표가 존재 |
| 5 | `docs/03-design.md` 작성 | 결정 표 8개가 "선택/대안/근거/트레이드오프" 형식으로 채워짐 |
| 6 | `docs/04-tasks.md` 작성 | Phase 1/2/3 체크리스트가 모두 존재 (본 문서) |
| 7 | `docs/05-conventions.md` 작성 | 명명/금지 5개/테스트/커밋 규칙이 모두 정의됨 |
| 8 | Git remote 연결 확인 | `git remote -v` 가 `origin` 출력 |
| 9 | `.gitignore` 정비 | Python·Node·IDE·`.env` 기본 무시 항목 포함 |
| 10 | Phase 1 첫 커밋 | `git log -1` 메시지가 `docs: Phase 1 설계 문서 7종 작성` |

---

## Phase 2 — 백엔드 (10단계) ✅ 완료
> 목표: `backend/` 디렉토리에 FastAPI 기반 CRUD API 5개를 구현하고 Swagger로 확인한다.
> 검증: 10/10 단계 통과 — 커밋 `de42b05` + 매트릭스 보강분. `pytest` 정상 9 / 400 8 / 404 4 = **19/19 통과**, `/docs` 에 5개 엔드포인트 노출 확인.

| # | 작업 | 검증 방법 |
|---|---|---|
| 1 | `backend/` 생성 + 의존성 정의 (`requirements.txt`) | `fastapi`, `uvicorn`, `sqlalchemy` 명시 / `pip install -r` 성공 |
| 2 | `.env.example` 작성 (`DATABASE_URL` 등) | 시크릿은 비워둔 상태로 키만 존재 |
| 3 | SQLAlchemy `Task` 모델 작성 | `02-specs` 7필드와 1:1 일치, 타입 확인 |
| 4 | DB 초기화 + 마이그레이션 | 앱 부팅 시 SQLite 파일 자동 생성, 테이블 1개 확인 |
| 5 | Pydantic 스키마 (`TaskCreate`/`TaskUpdate`/`TaskOut` 등) | `title` 누락 시 422/400, `status` enum 위반 시 400 |
| 6 | `POST /api/tasks` 구현 | `curl` 로 201 + 생성된 객체 응답 |
| 7 | `GET /api/tasks` 목록 구현 | 응답에 `description` 필드 **없음** |
| 8 | `GET /api/tasks/{id}` + 404 | `description` 포함, 없는 id는 404 |
| 9 | `PUT /api/tasks/{id}` 부분 수정 | 일부 필드만 보내고 GET으로 변경분만 반영 확인 |
| 10 | `DELETE /api/tasks/{id}` + Swagger 점검 | 204 응답 + 이후 GET 404 / `/docs` 에 5개 엔드포인트 노출 |

---

## Phase 3 — 프론트 (8단계) ✅ 완료
> 목표: `frontend/` 디렉토리에 HTML + Vanilla JS + Tailwind CDN으로 메인 화면을 구축하고 백엔드와 연결한 뒤 GitHub에 push 한다.
> 검증: 코드/자동 검증 완료 — 커밋 `4b38b3f` (UI 구현, `origin/main` push 완료) + 후속 `dayjs` 통합. 시각/반응형 수동 검증은 사용자 브라우저로 진행.

| # | 작업 | 검증 방법 |
|---|---|---|
| 1 | `frontend/index.html` 골격 + Tailwind CDN | 브라우저로 열어 빈 화면이 에러 없이 표시 |
| 2 | UI 토큰 적용 (`rounded-xl`/`shadow-lg`/`backdrop-blur`/시스템 폰트/터치 ≥44px) | 시안 카드 1개가 Mac OS 톤으로 보임 |
| 3 | 테마 토글 + `localStorage('theme')` | 토글 즉시 반영 + 새로고침 후에도 유지, OS 기본값 존중 |
| 4 | 추가 폼 (`title`/`due_at`/`status`) → `POST /api/tasks` | 제출 후 목록에 즉시 카드 추가 |
| 5 | 목록 카드 (status 배지 + `D-N HH:MM`) | 3개 상태 색상 구분 + 마감 표기 정확 (지난 마감은 `D+N`) |
| 6 | 카드 클릭 → 수정 모달 → `PUT /api/tasks/{id}` | 모달에서 수정 저장 시 카드가 즉시 갱신 |
| 7 | 휴지통 → 확인 다이얼로그 → `DELETE /api/tasks/{id}` | 확인 시 카드 제거, 새로고침 후에도 제거 유지 |
| 8 | 360px 반응형 확인 + `git push` | DevTools 360px에서 레이아웃 무너짐 없음 / `origin/main` 최신 |

def test_create_task_returns_201(client):
    response = client.post("/api/tasks", json={"title": "first task"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "first task"
    assert data["status"] == "todo"
    assert "id" in data
    assert "description" in data  # 단건/생성 응답에는 description 포함


def test_create_task_missing_title_returns_400(client):
    response = client.post("/api/tasks", json={})
    assert response.status_code == 400


def test_create_task_blank_title_returns_400(client):
    response = client.post("/api/tasks", json={"title": ""})
    assert response.status_code == 400


def test_create_task_title_too_long_returns_400(client):
    response = client.post("/api/tasks", json={"title": "x" * 201})
    assert response.status_code == 400


def test_create_task_invalid_status_returns_400(client):
    response = client.post(
        "/api/tasks", json={"title": "x", "status": "INVALID"}
    )
    assert response.status_code == 400


def test_create_task_invalid_due_at_returns_400(client):
    response = client.post(
        "/api/tasks", json={"title": "x", "due_at": "not-a-date"}
    )
    assert response.status_code == 400


def test_create_task_accepts_iso8601_due_at(client):
    response = client.post(
        "/api/tasks",
        json={"title": "with due", "due_at": "2026-05-12T18:00:00Z"},
    )
    assert response.status_code == 201
    assert response.json()["due_at"] is not None


def test_list_tasks_excludes_description(client):
    client.post("/api/tasks", json={"title": "a", "description": "secret"})
    response = client.get("/api/tasks")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert "description" not in items[0]


def test_get_task_includes_description(client):
    created = client.post(
        "/api/tasks", json={"title": "a", "description": "hello"}
    ).json()
    response = client.get(f"/api/tasks/{created['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "hello"


def test_get_task_missing_returns_404(client):
    response = client.get("/api/tasks/9999")
    assert response.status_code == 404


def test_update_task_partial_preserves_unspecified_fields(client):
    created = client.post(
        "/api/tasks", json={"title": "before", "description": "keep"}
    ).json()
    response = client.put(
        f"/api/tasks/{created['id']}", json={"status": "done"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"
    assert data["title"] == "before"
    assert data["description"] == "keep"


def test_update_task_invalid_status_returns_400(client):
    created = client.post("/api/tasks", json={"title": "x"}).json()
    response = client.put(
        f"/api/tasks/{created['id']}", json={"status": "INVALID"}
    )
    assert response.status_code == 400


def test_update_task_invalid_due_at_returns_400(client):
    created = client.post("/api/tasks", json={"title": "x"}).json()
    response = client.put(
        f"/api/tasks/{created['id']}", json={"due_at": "not-a-date"}
    )
    assert response.status_code == 400


def test_update_task_blank_title_returns_400(client):
    created = client.post("/api/tasks", json={"title": "x"}).json()
    response = client.put(f"/api/tasks/{created['id']}", json={"title": ""})
    assert response.status_code == 400


def test_update_task_missing_returns_404(client):
    response = client.put("/api/tasks/9999", json={"status": "done"})
    assert response.status_code == 404


def test_delete_task_returns_204_then_404(client):
    created = client.post("/api/tasks", json={"title": "to delete"}).json()
    response = client.delete(f"/api/tasks/{created['id']}")
    assert response.status_code == 204
    follow_up = client.get(f"/api/tasks/{created['id']}")
    assert follow_up.status_code == 404


def test_delete_task_missing_returns_404(client):
    response = client.delete("/api/tasks/9999")
    assert response.status_code == 404


def test_export_empty_returns_envelope(client):
    response = client.get("/api/tasks/export")
    assert response.status_code == 200
    payload = response.json()
    assert payload["version"] == 1
    assert payload["count"] == 0
    assert payload["tasks"] == []
    assert "exported_at" in payload
    cd = response.headers.get("content-disposition", "")
    assert "attachment" in cd.lower()
    assert "taskflow-export" in cd


def test_export_includes_all_task_fields(client):
    client.post(
        "/api/tasks",
        json={"title": "alpha", "description": "first", "status": "todo"},
    )
    client.post("/api/tasks", json={"title": "beta", "status": "done"})
    response = client.get("/api/tasks/export")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2
    item = payload["tasks"][0]
    for key in (
        "id",
        "title",
        "description",
        "status",
        "due_at",
        "created_at",
        "updated_at",
    ):
        assert key in item


def test_export_path_does_not_collide_with_task_id(client):
    # /api/tasks/export 는 /api/tasks/{task_id} 보다 먼저 매칭되어야 함
    response = client.get("/api/tasks/export")
    assert response.status_code == 200
    body = response.json()
    # 단건 조회 응답이 아니라 export 봉투인지 확인
    assert "version" in body and "tasks" in body

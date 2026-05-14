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

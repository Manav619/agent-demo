from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import database
from app.main import app


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "test_tasks.db"
    monkeypatch.setenv("TASKS_DB_PATH", str(db_path))
    database.init_db()

    with TestClient(app) as test_client:
        yield test_client


def test_create_task(client: TestClient):
    response = client.post(
        "/tasks",
        json={"title": "Test task", "description": "Task description", "completed": False},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Test task"
    assert data["description"] == "Task description"
    assert data["completed"] is False
    assert data["created_at"]


def test_list_tasks(client: TestClient):
    client.post("/tasks", json={"title": "Task 1", "description": "First", "completed": False})
    client.post("/tasks", json={"title": "Task 2", "description": "Second", "completed": True})

    response = client.get("/tasks")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task 1"
    assert data[1]["title"] == "Task 2"


def test_get_task_by_id(client: TestClient):
    created = client.post("/tasks", json={"title": "Task", "description": "Desc", "completed": False})
    task_id = created.json()["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Task"


def test_get_task_not_found(client: TestClient):
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_task(client: TestClient):
    created = client.post("/tasks", json={"title": "Before", "description": "Desc", "completed": False})
    task_id = created.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "After", "description": "Updated", "completed": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "After"
    assert data["description"] == "Updated"
    assert data["completed"] is True


def test_update_task_not_found(client: TestClient):
    response = client.put("/tasks/999", json={"title": "x", "description": None, "completed": False})

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_delete_task(client: TestClient):
    created = client.post("/tasks", json={"title": "To delete", "description": "Desc", "completed": False})
    task_id = created.json()["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_delete_task_not_found(client: TestClient):
    response = client.delete("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

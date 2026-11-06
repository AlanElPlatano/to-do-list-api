import pytest

import app as app_module
import db


@pytest.fixture
def client(monkeypatch):
    # Sustituye la base de datos por una lista en memoria: las pruebas no tocan AWS
    tasks = []

    def fake_create_task(title, done):
        task = {"id": len(tasks) + 1, "title": title, "done": done}
        tasks.append(task)
        return task

    monkeypatch.setattr(db, "init_db", lambda: None)
    monkeypatch.setattr(db, "list_tasks", lambda: list(tasks))
    monkeypatch.setattr(db, "create_task", fake_create_task)

    return app_module.create_app().test_client()


def test_post_task_and_list_it(client):
    response = client.post("/tasks", json={"title": "Escribir pruebas"})

    assert response.status_code == 201
    assert response.get_json() == {"id": 1, "title": "Escribir pruebas", "done": False}
    assert client.get("/tasks").get_json() == [response.get_json()]


@pytest.mark.parametrize("payload", [{"done": True}, {"title": 123}, {"title": "   "}])
def test_post_task_with_invalid_title_is_rejected(client, payload):
    response = client.post("/tasks", json=payload)

    assert response.status_code == 400
    assert client.get("/tasks").get_json() == []


def test_version_reads_environment_variable(client, monkeypatch):
    monkeypatch.setenv("APP_VERSION", "v1.2.3")

    response = client.get("/version")

    assert response.status_code == 200
    assert response.get_json() == {"version": "v1.2.3"}

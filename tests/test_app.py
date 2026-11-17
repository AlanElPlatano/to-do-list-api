import psycopg2
import pytest

import app as app_module
import db
import metrics


@pytest.fixture
def published_metrics(monkeypatch):
    # Registra las métricas en una lista en lugar de mandarlas a CloudWatch
    published = []
    monkeypatch.setattr(metrics, "put_count", lambda name, value=1: published.append(name))
    return published


@pytest.fixture
def client(monkeypatch, published_metrics):
    # Sustituye la base de datos por una lista en memoria: las pruebas no tocan AWS
    tasks = []

    def fake_create_task(title, done):
        task = {"id": len(tasks) + 1, "title": title, "done": done}
        tasks.append(task)
        return task

    monkeypatch.setattr(db, "init_db", lambda: None)
    monkeypatch.setattr(db, "ping", lambda: None)
    monkeypatch.setattr(db, "list_tasks", lambda: list(tasks))
    monkeypatch.setattr(db, "create_task", fake_create_task)

    return app_module.create_app().test_client()


def test_post_task_and_list_it(client, published_metrics):
    response = client.post("/tasks", json={"title": "Escribir pruebas"})

    assert response.status_code == 201
    assert response.get_json() == {"id": 1, "title": "Escribir pruebas", "done": False}
    assert client.get("/tasks").get_json() == [response.get_json()]
    assert published_metrics == ["TasksCreated"]


@pytest.mark.parametrize("payload", [{"done": True}, {"title": 123}, {"title": "   "}])
def test_post_task_with_invalid_title_is_rejected(client, payload, published_metrics):
    response = client.post("/tasks", json=payload)

    assert response.status_code == 400
    assert client.get("/tasks").get_json() == []
    assert published_metrics == []


def test_version_reads_environment_variable(client, monkeypatch):
    monkeypatch.setenv("APP_VERSION", "v1.2.3")

    response = client.get("/version")

    assert response.status_code == 200
    assert response.get_json() == {"version": "v1.2.3"}


def test_health_reports_database_ok(client, monkeypatch):
    monkeypatch.setenv("APP_VERSION", "v1.2.3")

    response = client.get("/health")

    body = response.get_json()
    assert response.status_code == 200
    assert body["database"] == "OK"
    assert body["version"] == "v1.2.3"
    assert body["timestamp"]


def test_health_reports_database_fail(client, monkeypatch):
    def broken_ping():
        raise psycopg2.OperationalError("RDS detenida")

    monkeypatch.setattr(db, "ping", broken_ping)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.get_json()["database"] == "FAIL"


def test_database_error_is_counted_and_returns_503(monkeypatch, published_metrics):
    def unreachable_database():
        raise psycopg2.OperationalError("RDS detenida")

    monkeypatch.setattr(db, "init_db", lambda: None)
    monkeypatch.setattr(db, "get_connection", unreachable_database)
    client = app_module.create_app().test_client()

    response = client.get("/tasks")

    assert response.status_code == 503
    assert published_metrics == ["DatabaseErrors"]

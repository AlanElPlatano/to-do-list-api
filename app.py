import os
from datetime import datetime, timezone

import psycopg2
from flask import Flask, jsonify, request

import db
import metrics


def get_version():
    # La versión la define el despliegue (tag del release) en una variable de ambiente
    return os.environ.get("APP_VERSION", "dev")


def create_app():
    app = Flask(__name__)
    db.init_db()

    @app.errorhandler(psycopg2.Error)
    def database_error(error):
        return jsonify({"error": "No se pudo acceder a la base de datos"}), 503

    @app.get("/version")
    def version():
        return jsonify({"version": get_version()})

    @app.get("/health")
    def health():
        try:
            db.ping()
            database = "OK"
        except psycopg2.Error:
            database = "FAIL"

        body = {
            "database": database,
            "version": get_version(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return jsonify(body), 200 if database == "OK" else 503

    @app.get("/tasks")
    def list_tasks():
        return jsonify(db.list_tasks())

    @app.post("/tasks")
    def create_task():
        data = request.get_json(silent=True) or {}
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            return jsonify({"error": "El campo 'title' es obligatorio y debe ser texto"}), 400

        task = db.create_task(title.strip(), bool(data.get("done", False)))
        metrics.put_count("TasksCreated")
        return jsonify(task), 201

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=8000)

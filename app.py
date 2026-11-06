import os

from flask import Flask, jsonify, request

import db


def create_app():
    app = Flask(__name__)
    db.init_db()

    @app.get("/version")
    def version():
        # La versión la define el despliegue (tag del release) en una variable de ambiente
        return jsonify({"version": os.environ.get("APP_VERSION", "dev")})

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
        return jsonify(task), 201

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=8000)

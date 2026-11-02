import json
import os

import boto3
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request

app = Flask(__name__)


def load_db_config():
    # Las credenciales viven en Secrets Manager; la EC2 las lee con su rol de IAM
    client = boto3.client("secretsmanager", region_name=os.environ["AWS_REGION"])
    secret = client.get_secret_value(SecretId=os.environ["DB_SECRET_NAME"])
    return json.loads(secret["SecretString"])


DB_CONFIG = load_db_config()


def get_connection():
    return psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["username"],
        password=DB_CONFIG["password"],
        cursor_factory=RealDictCursor,
    )


def init_db():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
            """
        )


init_db()


@app.get("/tasks")
def list_tasks():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
        return jsonify(cur.fetchall())


@app.post("/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "El campo 'title' es obligatorio"}), 400

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done",
            (title, bool(data.get("done", False))),
        )
        task = cur.fetchone()
    return jsonify(task), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

import functools
import json
import os

import boto3
import psycopg2
from psycopg2.extras import RealDictCursor


@functools.cache
def get_db_config():
    # Las credenciales viven en Secrets Manager; la EC2 las lee con su rol de IAM
    client = boto3.client("secretsmanager", region_name=os.environ["AWS_REGION"])
    secret = client.get_secret_value(SecretId=os.environ["DB_SECRET_NAME"])
    return json.loads(secret["SecretString"])


def get_connection():
    config = get_db_config()
    return psycopg2.connect(
        host=config["host"],
        port=config["port"],
        dbname=config["dbname"],
        user=config["username"],
        password=config["password"],
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


def list_tasks():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
        return cur.fetchall()


def create_task(title, done):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done",
            (title, done),
        )
        return cur.fetchone()

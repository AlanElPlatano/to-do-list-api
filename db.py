import contextlib
import functools
import json
import os

import boto3
import psycopg2
from psycopg2.extras import RealDictCursor

import metrics


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
        # Sin límite, una base apagada deja la petición colgada hasta que gunicorn la mata
        connect_timeout=5,
    )


@contextlib.contextmanager
def cursor():
    # Toda lectura o escritura pasa por aquí, así cada error de RDS queda contado
    try:
        with contextlib.closing(get_connection()) as conn, conn, conn.cursor() as cur:
            yield cur
    except psycopg2.Error:
        metrics.put_count("DatabaseErrors")
        raise


def init_db():
    with cursor() as cur:
        # Cada worker de gunicorn corre esto al arrancar; sin el lock, dos CREATE TABLE
        # simultáneos chocan en el catálogo de PostgreSQL aunque usen IF NOT EXISTS
        cur.execute("SELECT pg_advisory_xact_lock(1)")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
            """
        )


def ping():
    with cursor() as cur:
        cur.execute("SELECT 1")


def list_tasks():
    with cursor() as cur:
        cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
        return cur.fetchall()


def create_task(title, done):
    with cursor() as cur:
        cur.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done",
            (title, done),
        )
        return cur.fetchone()

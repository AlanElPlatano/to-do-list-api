from flask import Flask, jsonify, request

app = Flask(__name__)

# Almacenamiento en memoria: se pierde al reiniciar la app
tasks = []


@app.get("/tasks")
def list_tasks():
    return jsonify(tasks)


@app.post("/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "El campo 'title' es obligatorio"}), 400

    task = {"id": len(tasks) + 1, "title": title, "done": bool(data.get("done", False))}
    tasks.append(task)
    return jsonify(task), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

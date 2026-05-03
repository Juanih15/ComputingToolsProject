from flask import Flask, jsonify, request
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId
from datetime import datetime, timezone
import socket
import os

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongo:27017/")
DB_NAME = "taskdb"

def get_db():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    return client[DB_NAME]


@app.route("/")
def home():
    return jsonify({
        "app": "USF Flask-Mongo Pipeline",
        "host": socket.gethostname(),
        "endpoints": {
            "GET /": "this page",
            "GET /health": "service + DB health check",
            "GET /tasks": "list all tasks",
            "POST /tasks": "create a task (JSON: {title, description?})",
            "GET /tasks/<id>": "get a single task",
            "PUT /tasks/<id>": "update a task (JSON: {title?, description?})",
            "DELETE /tasks/<id>": "delete a task",
        }
    })


@app.route("/health")
def health():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        mongo_status = "connected"
    except ConnectionFailure:
        mongo_status = "unreachable"
        return jsonify({"status": "degraded", "mongo": mongo_status}), 503

    return jsonify({"status": "ok", "mongo": mongo_status})


@app.route("/tasks", methods=["GET"])
def list_tasks():
    db = get_db()
    tasks = []
    for doc in db.tasks.find().sort("created_at", -1):
        tasks.append({
            "id": str(doc["_id"]),
            "title": doc["title"],
            "description": doc.get("description", ""),
            "created_at": doc["created_at"].isoformat(),
        })
    return jsonify(tasks)


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)
    if not data or not data.get("title"):
        return jsonify({"error": "title is required"}), 400

    db = get_db()
    doc = {
        "title": data["title"],
        "description": data.get("description", ""),
        "created_at": datetime.now(timezone.utc),
    }
    result = db.tasks.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc["created_at"] = doc["created_at"].isoformat()
    del doc["_id"]
    return jsonify(doc), 201


@app.route("/tasks/<task_id>", methods=["GET"])
def get_task(task_id):
    db = get_db()
    try:
        doc = db.tasks.find_one({"_id": ObjectId(task_id)})
    except Exception:
        return jsonify({"error": "invalid task id"}), 400

    if not doc:
        return jsonify({"error": "task not found"}), 404

    return jsonify({
        "id": str(doc["_id"]),
        "title": doc["title"],
        "description": doc.get("description", ""),
        "created_at": doc["created_at"].isoformat(),
    })


# Added PUT endpoint to update existing tasks
# Allows partial updates - you can update just title, just description, or both
@app.route("/tasks/<task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "no data provided"}), 400

    db = get_db()
    try:
        # Build update dictionary with only the fields provided
        update_fields = {}
        if "title" in data:
            update_fields["title"] = data["title"]
        if "description" in data:
            update_fields["description"] = data["description"]
        
        if not update_fields:
            return jsonify({"error": "no valid fields to update"}), 400
        
        # Update only the specified fields using MongoDB $set operator
        result = db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": update_fields}
        )
    except Exception:
        return jsonify({"error": "invalid task id"}), 400

    if result.matched_count == 0:
        return jsonify({"error": "task not found"}), 404

    # Fetch and return the updated task
    doc = db.tasks.find_one({"_id": ObjectId(task_id)})
    return jsonify({
        "id": str(doc["_id"]),
        "title": doc["title"],
        "description": doc.get("description", ""),
        "created_at": doc["created_at"].isoformat(),
    })


@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    db = get_db()
    try:
        result = db.tasks.delete_one({"_id": ObjectId(task_id)})
    except Exception:
        return jsonify({"error": "invalid task id"}), 400

    if result.deleted_count == 0:
        return jsonify({"error": "task not found"}), 404

    return jsonify({"deleted": task_id})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

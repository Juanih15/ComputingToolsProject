from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://admin:ChangeMe123@mongo:27017/?authSource=admin")
client = MongoClient(MONGO_URI)
db = client["flask_db"]

@app.route("/")
def home():
    db.stats.update_one(
        {"_id": "hits"},
        {"$inc": {"count": 1}},
        upsert=True
    )
    count = db.stats.find_one({"_id": "hits"})["count"]
    return f"<h1>Flask + MongoDB Pipeline</h1><p>Page hits: {count}</p>"

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
from flask import Flask, jsonify
import socket

app = Flask(__name__)

@app.route("/")
def home():
    return f"<h1>USF Flask App</h1><p>Running on host: {socket.gethostname()}</p>"

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
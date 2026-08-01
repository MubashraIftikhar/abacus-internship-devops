from flask import Flask, jsonify, render_template
import socket, os, datetime

app = Flask(__name__)

POD_NAME  = os.environ.get("POD_NAME", socket.gethostname())
POD_IP    = os.environ.get("POD_IP", "unknown")
NODE_NAME = os.environ.get("NODE_NAME", "unknown")
NAMESPACE = os.environ.get("POD_NAMESPACE", "default")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/info")
def info():
    return jsonify({
        "pod_name": POD_NAME,
        "pod_ip": POD_IP,
        "node_name": NODE_NAME,
        "namespace": NAMESPACE,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    })

@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

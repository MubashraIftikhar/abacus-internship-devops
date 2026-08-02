#!/usr/bin/env python3
"""
Tiny auth API. Every 4xx below is a REAL response to a REAL request -
nothing here is randomly generated. Error lines are appended to
/var/log/app/error.log in plain text so filebeat can ship just the
message with no extra fields.

Endpoints:
  POST /login   {"username": "...", "password": "..."}
                -> 200 + token on success
                -> 401 "invalid auth" on wrong username/password

  GET  /orders  Header: Authorization: Bearer <token>
                -> 200 on valid token
                -> 401 if header missing/malformed
                -> 403 if token present but not valid

  anything else -> 404
"""
import os
import time
import uuid
from datetime import datetime, timezone
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Login Test Page</title>
  <style>
    body { font-family: sans-serif; max-width: 400px; margin: 60px auto; }
    input { display: block; width: 100%; margin: 8px 0; padding: 8px; box-sizing: border-box; }
    button { padding: 8px 16px; margin-top: 8px; }
    #result { margin-top: 16px; padding: 10px; white-space: pre-wrap; font-family: monospace; }
    .ok { background: #e6ffed; border: 1px solid #2ecc71; }
    .err { background: #ffe6e6; border: 1px solid #e74c3c; }
  </style>
</head>
<body>
  <h2>Login test</h2>
  <p>Try <code>admin / S3cure!Pass</code> (success) or anything else (401, logged as an error).</p>
  <input id="username" placeholder="username" value="admin">
  <input id="password" placeholder="password" type="password">
  <button onclick="doLogin()">Login</button>
  <button onclick="doOrders()">Call /orders (no token)</button>
  <button onclick="doNotFound()">Hit unknown route (404)</button>
  <div id="result"></div>

<script>
async function show(resp, data) {
  const el = document.getElementById('result');
  el.className = resp.ok ? 'ok' : 'err';
  el.textContent = 'HTTP ' + resp.status + '\\n' + JSON.stringify(data, null, 2);
}
async function doLogin() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const resp = await fetch('/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, password})
  });
  show(resp, await resp.json());
}
async function doOrders() {
  const resp = await fetch('/orders');
  show(resp, await resp.json());
}
async function doNotFound() {
  const resp = await fetch('/this-route-does-not-exist');
  show(resp, await resp.json());
}
</script>
</body>
</html>
"""

LOG_FILE = "/var/log/app/error.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# demo user store: username -> password
USERS = {
    "admin": "S3cure!Pass",
    "alice": "alicepw123",
}

# very small in-memory session store: token -> username
SESSIONS = {}


def log_event(status, level, path, detail, client_ip):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    line = f"{ts} {level} {status} {path} - {detail} (client={client_ip})"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line, flush=True)


@app.route("/", methods=["GET"])
def index():
    return Response(LOGIN_PAGE, mimetype="text/html")


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        log_event(400, "ERROR", "/login", "Bad Request - missing username or password", request.remote_addr)
        return jsonify({"error": "username and password required"}), 400

    if USERS.get(username) != password:
        log_event(401, "ERROR", "/login", "Unauthorized - invalid username or password", request.remote_addr)
        return jsonify({"error": "invalid credentials"}), 401

    token = str(uuid.uuid4())
    SESSIONS[token] = username
    log_event(200, "INFO", "/login", "Login successful", request.remote_addr)
    return jsonify({"token": token}), 200


@app.route("/orders", methods=["GET"])
def orders():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        log_event(401, "ERROR", "/orders", "Unauthorized - missing or malformed Authorization header", request.remote_addr)
        return jsonify({"error": "missing bearer token"}), 401

    token = auth.split(" ", 1)[1]
    if token not in SESSIONS:
        log_event(403, "ERROR", "/orders", "Forbidden - invalid or expired token", request.remote_addr)
        return jsonify({"error": "invalid token"}), 403

    log_event(200, "INFO", "/orders", "Orders retrieved successfully", request.remote_addr)
    return jsonify({"orders": ["order-1", "order-2"]}), 200


@app.errorhandler(404)
def not_found(e):
    log_event(404, "ERROR", request.path, "Not Found - requested resource does not exist", request.remote_addr)
    return jsonify({"error": "not found"}), 404


if __name__ == "__main__":
    open(LOG_FILE, "a").close()
    app.run(host="0.0.0.0", port=5000)

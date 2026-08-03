from flask import Flask, request, jsonify, render_template_string
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
import random

app = Flask(__name__)

# --- Metrics ---
LOGIN_ATTEMPTS = Counter('login_attempts_total', 'Total login attempts')
LOGIN_SUCCESS = Counter('login_success_total', 'Total successful logins')
LOGIN_FAILURE = Counter('login_failure_total', 'Total failed logins', ['reason'])
LOGIN_LATENCY = Histogram('login_request_duration_seconds', 'Time taken to process login requests')
ACTIVE_SESSIONS = Gauge('active_sessions', 'Currently active logged-in sessions')

# Fake user DB
USERS = {
    "admin": "password123",
    "user1": "letmein"
}

sessions = set()

FORM_PAGE = """
<!doctype html>
<html>
<head><title>Login Demo</title></head>
<body style="font-family: sans-serif; max-width: 400px; margin: 60px auto;">
    <h2>Login Demo App</h2>
    <form method="POST" action="/login">
        <label>Username:</label><br>
        <input type="text" name="username" style="width:100%; padding:8px; margin:6px 0;"><br>
        <label>Password:</label><br>
        <input type="password" name="password" style="width:100%; padding:8px; margin:6px 0;"><br><br>
        <button type="submit" style="padding:8px 16px;">Login</button>
    </form>
    <p>{{ message }}</p>
    <hr>
    <p>Try: admin/password123, user1/letmein, or wrong credentials.</p>
    <p><a href="/metrics">View Prometheus metrics</a></p>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(FORM_PAGE, message="")

@app.route('/login', methods=['POST'])
def login():
    start = time.time()
    LOGIN_ATTEMPTS.inc()

    # Support both form submissions (browser) and JSON (curl)
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form

    username = data.get('username')
    password = data.get('password')

    time.sleep(random.uniform(0.05, 0.3))

    if not username or not password:
        LOGIN_FAILURE.labels(reason='missing_fields').inc()
        LOGIN_LATENCY.observe(time.time() - start)
        msg = "Error: username and password required"
    elif username in USERS and USERS[username] == password:
        sessions.add(username)
        ACTIVE_SESSIONS.set(len(sessions))
        LOGIN_SUCCESS.inc()
        LOGIN_LATENCY.observe(time.time() - start)
        msg = f"Welcome, {username}!"
    else:
        reason = 'bad_password' if username in USERS else 'unknown_user'
        LOGIN_FAILURE.labels(reason=reason).inc()
        LOGIN_LATENCY.observe(time.time() - start)
        msg = "Error: invalid credentials"

    # If browser form submission, show the message on the page
    if not request.is_json:
        return render_template_string(FORM_PAGE, message=msg)

    # If JSON (curl/API), return JSON as before
    status_code = 200 if "Welcome" in msg else (400 if "required" in msg else 401)
    return jsonify({"message": msg}), status_code

@app.route('/logout', methods=['POST'])
def logout():
    data = request.get_json(silent=True) or request.form
    username = data.get('username')
    if username in sessions:
        sessions.discard(username)
        ACTIVE_SESSIONS.set(len(sessions))
        return jsonify({"status": "ok", "message": f"{username} logged out"}), 200
    return jsonify({"status": "error", "message": "not logged in"}), 400

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

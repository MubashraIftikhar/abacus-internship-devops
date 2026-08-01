import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
CORS(app)

DB_HOST = os.environ.get("DB_HOST", "mysql-service")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_USER = os.environ.get("DB_USER", "app_user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "app_password")
DB_NAME = os.environ.get("DB_NAME", "student_db")


def get_connection(retries=10, delay=3):
    last_err = None
    for attempt in range(retries):
        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
            )
            return conn
        except Error as e:
            last_err = e
            print(f"[attempt {attempt+1}] DB not ready yet: {e}")
            time.sleep(delay)
    raise last_err


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    roll_no = (data.get("roll_no") or "").strip()

    if not name or not roll_no:
        return jsonify({"error": "name and roll_no are required"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, roll_no) VALUES (%s, %s)",
            (name, roll_no),
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"id": new_id, "name": name, "roll_no": roll_no}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "roll_no already exists"}), 409
    except Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/students", methods=["GET"])
def list_students():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, roll_no FROM students ORDER BY id")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

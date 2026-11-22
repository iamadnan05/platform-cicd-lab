import os
from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)


def get_db_status():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return "not_configured"
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    cur.close()
    conn.close()
    return "connected"


@app.route("/")
def home():
    return jsonify({"service": "platform-lab-api", "status": "running"}), 200


@app.route("/health")
def health():
    try:
        db_status = get_db_status()
        return jsonify({"status": "healthy", "database": db_status}), 200
    except Exception as err:
        return jsonify({"status": "unhealthy", "error": str(err)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

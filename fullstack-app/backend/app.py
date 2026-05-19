from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")


# -------------------------
# DATABASE CONNECTION
# -------------------------
def get_conn():
    if not DATABASE_URL:
        print("❌ DATABASE_URL not set")
        return None
    return psycopg2.connect(DATABASE_URL)


# -------------------------
# INIT DATABASE
# -------------------------
def init_db():
    conn = get_conn()
    if conn is None:
        return

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


# -------------------------
# RUN INIT BEFORE FIRST REQUEST
# -------------------------
@app.before_first_request
def setup():
    init_db()


# -------------------------
# ROUTES
# -------------------------

@app.route("/", methods=["GET"])
def home():
    return "Backend работает!"


@app.route("/api/data", methods=["GET"])
def get_data():
    conn = get_conn()
    if conn is None:
        return jsonify({"error": "No database connection"}), 500

    cur = conn.cursor()
    cur.execute("SELECT id, text FROM items")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    result = [{"id": r[0], "text": r[1]} for r in rows]

    return jsonify(result)


@app.route("/api/data", methods=["POST"])
def add_data():
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text'"}), 400

    conn = get_conn()
    if conn is None:
        return jsonify({"error": "No database connection"}), 500

    cur = conn.cursor()

    cur.execute(
        "INSERT INTO items (text) VALUES (%s) RETURNING id",
        (data["text"],)
    )

    item_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "id": item_id,
        "text": data["text"]
    })


@app.route("/api/data/<int:item_id>", methods=["DELETE"])
def delete_data(item_id):
    conn = get_conn()
    if conn is None:
        return jsonify({"error": "No database connection"}), 500

    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id=%s", (item_id,))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "deleted"})


# -------------------------
# RUN SERVER
# -------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
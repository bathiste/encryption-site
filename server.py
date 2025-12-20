from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit, disconnect
import secrets
import string
import logging
import os

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(16)
socketio = SocketIO(app, cors_allowed_origins="*")

# ------------------ USERS ------------------

def gen(n=10):
    return "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(n))

USER1 = f"user_{gen(4)}"
PASS1 = gen(12)
USER2 = f"user_{gen(4)}"
PASS2 = gen(12)

USER_DB = {
    USER1: {"password": PASS1, "target": USER2},
    USER2: {"password": PASS2, "target": USER1},
}

online = {}

logging.info(f"USER A: {USER1} | PASS: {PASS1}")
logging.info(f"USER B: {USER2} | PASS: {PASS2}")

# ------------------ WEB ------------------

F1_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Slipstream F1</title>
<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
<style>
body { background:#0b0b0b; color:#eee; font-family:Arial }
header { background:#e10600; padding:20px; text-align:center }
#chat { max-width:800px; margin:40px auto }
#log { height:300px; background:#111; padding:10px; overflow-y:auto }
input, button { padding:10px; margin-top:10px; width:100% }
</style>
</head>
<body>
<header>
<h1>Slipstream F1</h1>
<p>Unofficial Formula One fan hub</p>
</header>

<div id="chat">
<input id="user" placeholder="Username">
<input id="pw" placeholder="Password" type="password">
<button onclick="login()">Login</button>

<div id="log"></div>
<input id="msg" placeholder="Message">
<button onclick="send()">Send</button>
</div>

<script>
const socket = io();
let logged = false;

function log(t) {
    const d = document.getElementById("log");
    d.innerHTML += t + "<br>";
    d.scrollTop = d.scrollHeight;
}

function login() {
    socket.emit("auth", {
        user: document.getElementById("user").value,
        pw: document.getElementById("pw").value
    });
}

function send() {
    if (!logged) return;
    socket.emit("message", document.getElementById("msg").value);
    document.getElementById("msg").value = "";
}

socket.on("auth_ok", () => {
    logged = true;
    log("[SYSTEM] Logged in");
});

socket.on("auth_fail", () => {
    log("[SYSTEM] Login failed");
});

socket.on("message", data => {
    log(data);
});
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(F1_HTML)

# ------------------ SOCKET EVENTS ------------------

@socketio.on("auth")
def auth(data):
    user = data.get("user")
    pw = data.get("pw")

    if USER_DB.get(user, {}).get("password") != pw:
        emit("auth_fail")
        disconnect()
        return

    online[user] = request.sid
    emit("auth_ok")
    logging.info(f"{user} connected")

@socketio.on("message")
def relay(msg):
    sender = None
    for u, sid in online.items():
        if sid == request.sid:
            sender = u
            break

    if not sender:
        return

    target = USER_DB[sender]["target"]
    target_sid = online.get(target)

    if target_sid:
        socketio.emit(
            "message",
            f"[{sender}] {msg}",
            to=target_sid
        )
    else:
        emit("message", "[SYSTEM] Target offline")

@socketio.on("disconnect")
def cleanup():
    for u in list(online):
        if online[u] == request.sid:
            del online[u]
            logging.info(f"{u} disconnected")

# ------------------ ENTRY ------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)

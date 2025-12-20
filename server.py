import socket
import threading
import secrets
import string

# --- MVP CONFIGURATION ---
def generate_credentials(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

# Generate 2 Users automatically
USER1_NAME = "user_" + generate_credentials(4)
USER1_PASS = generate_credentials(12)

USER2_NAME = "user_" + generate_credentials(4)
USER2_PASS = generate_credentials(12)

# Map them to each other
USER_DB = {
    USER1_NAME: {"password": USER1_PASS, "target": USER2_NAME},
    USER2_NAME: {"password": USER2_PASS, "target": USER1_NAME}
}

active_clients = {}

def handle_client(conn, addr):
    try:
        conn.send(b"AUTH_REQ")
        auth_data = conn.recv(1024).decode().split(":")
        
        if len(auth_data) != 2: return
        username, password = auth_data[0], auth_data[1]

        if username in USER_DB and USER_DB[username]["password"] == password:
            print(f"[AUTH] {username} logged in from {addr[0]}")
            active_clients[username] = conn
            conn.send(b"AUTH_SUCCESS")
            
            while True:
                message = conn.recv(4096)
                if not message: break
                
                target_user = USER_DB[username]["target"]
                if target_user in active_clients:
                    print(f"[RELAY] {username} -> {target_user} ({len(message)} bytes)")
                    active_clients[target_user].send(f"\n[{username}]: ".encode() + message + b"\nChat > ")
                else:
                    conn.send(b"\n[SYSTEM] Target user is currently offline.\nChat > ")
        else:
            print(f"[AUTH FAIL] Unauthorized access attempt from {addr[0]}")
            conn.send(b"AUTH_FAILED")
    except:
        pass
    finally:
        if 'username' in locals() and username in active_clients:
            del active_clients[username]
        conn.close()

def start_server():
    # Get Local IP
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 5555))
    server.listen(2)

    print("="*50)
    print(f"SECURECHAT SERVER ACTIVE")
    print(f"SERVER IP: {local_ip}")
    print("="*50)
    print(f"USER A: {USER1_NAME}  |  PASS: {USER1_PASS}")
    print(f"USER B: {USER2_NAME}  |  PASS: {USER2_PASS}")
    print(f"Targeting: {USER1_NAME} <--> {USER2_NAME}")
    print("="*50)

    while True:
        conn, addr = server.accept()
        print(f"[LOG] Connection from {addr[0]}")
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
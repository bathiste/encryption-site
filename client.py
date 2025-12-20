import socket
import threading

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(4096).decode()
            if not data:
                break
            print(data)
        except:
            break

def start_client():
    print("--- SECURECHAT CLIENT ---")
    ip = input("Server IP: ")
    port = int(input("Server Port (default 5555): ") or 5555)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((ip, port))

        if sock.recv(1024) != b"AUTH_REQ":
            print("Protocol error.")
            return

        user = input("Username: ")
        pw = input("Password: ")
        sock.sendall(f"{user}:{pw}".encode())

        if sock.recv(1024) != b"AUTH_SUCCESS":
            print("Login failed.")
            return

        print("[+] Logged in. Type 'quit' to exit.")

        threading.Thread(
            target=receive_messages,
            args=(sock,),
            daemon=True
        ).start()

        while True:
            msg = input()
            if msg.lower() == "quit":
                break
            sock.sendall(msg.encode())

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    start_client()

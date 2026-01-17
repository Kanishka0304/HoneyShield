import socket
import threading
from datetime import datetime

import paramiko
import requests

from app.config import settings


class HoneyShieldSSHServer(paramiko.ServerInterface):
    """Paramiko ServerInterface that always denies auth but logs attempts."""

    def __init__(self, client_addr):
        super().__init__()
        self.client_addr = client_addr
        self.event = threading.Event()

    def check_auth_password(self, username, password):  # type: ignore[override]
        source_ip = self.client_addr[0] if self.client_addr else "unknown"

        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "source_ip": source_ip,
            "username": username,
            "password": password,
            "port": settings.HONEYPOT_LISTEN_PORT,
            "protocol": "ssh",
            "success": False,
            "raw": None,
        }

        try:
            ingest_url = f"http://127.0.0.1:8000{settings.API_PREFIX}/ingest/ssh"
            requests.post(ingest_url, json=payload, timeout=2)
        except Exception:
            # We intentionally ignore failures here to keep honeypot lightweight.
            pass

        # Always fail authentication (honeypot only)
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):  # type: ignore[override]
        return "password"

    def check_channel_request(self, kind, chanid):  # type: ignore[override]
        # No real shell or channels allowed
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED


def handle_connection(client, addr):
    transport = paramiko.Transport(client)

    # Use a random in-memory host key for now (not persisted)
    host_key = paramiko.RSAKey.generate(2048)
    transport.add_server_key(host_key)

    server = HoneyShieldSSHServer(addr)

    try:
        transport.start_server(server=server)
    except paramiko.SSHException:
        transport.close()
        return

    # We don't accept any channels; just wait a bit then close.
    try:
        server.event.wait(5)
    finally:
        transport.close()


def run_honeypot():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((settings.HONEYPOT_LISTEN_HOST, settings.HONEYPOT_LISTEN_PORT))
    sock.listen(100)

    print(
        f"[HoneyShield Honeypot] Listening on {settings.HONEYPOT_LISTEN_HOST}:{settings.HONEYPOT_LISTEN_PORT}"
    )

    while True:
        client, addr = sock.accept()
        t = threading.Thread(target=handle_connection, args=(client, addr))
        t.daemon = True
        t.start()


if __name__ == "__main__":
    run_honeypot()

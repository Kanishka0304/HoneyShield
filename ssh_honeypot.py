import socket
import threading
import logging
import time

# Set up logging for the honeypot
logging.basicConfig(filename="honeypot_logs.txt", level=logging.INFO)

# Honeypot function for SSH service simulation (with authentication failure simulation)
def handle_ssh_connection(client_socket, client_address):
    logging.info(f"Connection attempt from {client_address} at {time.ctime()}")

    # Send fake SSH banner (mimicking an OpenSSH server)
    ssh_banner = b"SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.3\r\n"
    client_socket.send(ssh_banner)

    # Simulate SSH login process
    try:
        # Fake the SSH authentication request
        client_socket.recv(1024)  # Receive the initial SSH request (client sending SSH version)
        
        # Send an authentication prompt (username request)
        client_socket.send(b"SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.3\r\n")
        client_socket.send(b"Password: ")  # This is where the SSH server would prompt for a password
        
        # Simulate receiving the username and password (attacker tries to send a password)
        # (This is just for simulation, in a real honeypot, we would expect different behavior)
        password_attempt = client_socket.recv(1024).decode('utf-8').strip()  # Read password input
        
        # Log the attempted password (this would be helpful for analysis)
        logging.info(f"Received password attempt: {password_attempt} from {client_address}")

        # Simulate authentication failure
        # Normally, the SSH server would check the password. Here, we always fail the authentication.
        if password_attempt != "correct_password":
            response = b"Permission denied, please try again.\r\n"
            client_socket.send(response)
        else:
            # Simulate successful authentication (fake success message, just for realism)
            response = b"Welcome to the SSH server!\r\n"
            client_socket.send(response)

    except Exception as e:
        logging.error(f"Error in handling connection from {client_address}: {e}")
    
    # Simulate idle time or other interaction (optional)
    time.sleep(2)  # You can adjust this to simulate different attack scenarios
    
    # Log and close the connection
    logging.info(f"Closing connection from {client_address}")
    client_socket.close()

def start_ssh_honeypot(host, port):
    honeypot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    honeypot_socket.bind((host, port))
    honeypot_socket.listen(5)  # Listen for a maximum of 5 incoming connections
    logging.info(f"SSH Honeypot listening on {host}:{port}...")

    while True:
        # Accept incoming connection
        client_socket, client_address = honeypot_socket.accept()
        logging.info(f"Connection from {client_address} established.")

        # Handle each connection in a separate thread
        thread = threading.Thread(target=handle_ssh_connection, args=(client_socket, client_address))
        thread.start()

if __name__ == "__main__":
    start_ssh_honeypot('0.0.0.0', 22)  # Listens on all interfaces (0.0.0.0) on port 22


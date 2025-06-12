import socket
import threading
import os
import base64
import random

def handle_client_request(filename, client_address, server_socket):
    # Worker thread to handle the client's file transfer request
    # Randomly select a high-order port (50000 - 51000)
    port = random.randint(50000, 51000)
    try:
        # Check if the file exists
        if not os.path.exists(filename):
            response = f"ERR {filename} NOT_FOUND"
            server_socket.sendto(response.encode(), client_address)
            return

        # Get the file size
        file_size = os.path.getsize(filename)
        # Send an OK response containing the file name, size, and new port
        response = f"OK {filename} SIZE {file_size} PORT {port}"
        server_socket.sendto(response.encode(), client_address)

        # Create a new UDP socket for file transfer
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.bind(('', port))

        # Open the file to read data
        with open(filename, 'rb') as f:
            while True:
                # Receive the client's FILE request
                try:
                    data, client_address = client_socket.recvfrom(2048)
                    message = data.decode()
                    parts = message.split()

                    # Handle the FILE GET request
                    if parts[0] == "FILE" and parts[2] == "GET":
                        filename = parts[1]
                        start = int(parts[4])
                        end = int(parts[6])
                        # Read the data in the specified byte range
                        f.seek(start)
                        data_chunk = f.read(end - start + 1)
                        # Base64 encode the data
                        encoded_data = base64.b64encode(data_chunk).decode()
                        # Send the response
                        response = f"FILE {filename} OK START {start} END {end} DATA {encoded_data}"
                        client_socket.sendto(response.encode(), client_address)

                    # Handle the FILE CLOSE request
                    elif parts[0] == "FILE" and parts[2] == "CLOSE":
                        response = f"FILE {filename} CLOSE_OK"
                        client_socket.sendto(response.encode(), client_address)
                        break

                except socket.timeout:
                    continue  # Ignore the timeout and continue waiting for requests

        client_socket.close()

    except Exception as e:
        print(f"Thread processing error: {e}")
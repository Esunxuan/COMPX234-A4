import socket
import threading
import os
import base64
import random

def handle_client_request(filename, client_address, server_socket):
    """
        Handle client requests for file transfer in a dedicated thread.
        
        Args:
            filename (str): Name of the requested file.
            client_address (tuple): Client's address (host, port).
            server_socket (socket): Main server socket for initial communication.
        
        Steps:
            1. Validate file existence.
            2. Allocate a random high-order port for data transfer.
            3. Send initial response with file metadata.
            4. Handle segmented file requests until client closes connection.
        """
    
    
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

def main():
    """
        Main server function.
        
        Steps:
            1. Parse command-line arguments.
            2. Initialize main UDP socket.
            3. Listen for DOWNLOAD requests.
            4. Spawn threads to handle concurrent client requests.
    """

    # Parse the command-line arguments
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 UDPserver.py <port>")
        sys.exit(1)
    port = int(sys.argv[1])

    # Create the main UDP socket to listen for DOWNLOAD requests
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', port))
    print(f"Server started, listening on port {port}")

    # Main loop to handle client requests
    while True:
        try:
            data, client_address = server_socket.recvfrom(1024)
            message = data.decode()
            if message.startswith("DOWNLOAD"):
                filename = message.split()[1]
                # Create a new thread for each DOWNLOAD request
                thread = threading.Thread(target=handle_client_request, args=(filename, client_address, server_socket))
                thread.start()
                print(f"Processing client {client_address}'s request: {filename}")
        except Exception as e:
            print(f"Server error: {e}")

if __name__ == "__main__":
    main()
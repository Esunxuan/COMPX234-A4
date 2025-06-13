import socket
import sys
import base64
import time
import os

def send_and_receive(sock, message, server_address, timeout=1, max_retries=5):
    """
    Send a message to the server and wait for a response.
    Support timeout and retransmission mechanisms.

    Args:
        sock (socket.socket): The UDP socket used for communication.
        message (str): The message to be sent to the server.
        server_address (tuple): The address of the server (hostname, port).
        timeout (float): The initial timeout value in seconds. Default is 1 second.
        max_retries (int): The maximum number of retransmission attempts. Default is 5 times.

    Returns:
        str or None: The response from the server if successful, otherwise None.
    """
    retries = 0
    current_timeout = timeout
    while retries < max_retries:
        try:
            sock.settimeout(current_timeout)
            sock.sendto(message.encode(), server_address)
            print(f"Sent: {message}")
            data, _ = sock.recvfrom(2048)
            response = data.decode()
            print(f"Received: {response}")
            return response
        except socket.timeout:
            retries += 1
            current_timeout += 0.5  # Increase the timeout by 0.5 seconds for each retransmission
            print(f"Timeout, Retry {retries}/{max_retries}")
        except Exception as e:
            print(f"Error: {e}")
            break
    return None


def download_file(sock, filename, server_address):
    """
    Download a file from the server.

    Args:
        sock (socket.socket): The UDP socket used for communication.
        filename (str): The name of the file to be downloaded.
        server_address (tuple): The address of the server (hostname, port).

    Returns:
        bool: True if the file is successfully downloaded, otherwise False.
    """
    # Send a DOWNLOAD request
    request = f"DOWNLOAD {filename}"
    response = send_and_receive(sock, request, server_address)
    if not response or response.startswith("ERR"):
        print(f"File {filename} not found")
        return False

    # Parse the OK response
    parts = response.split()
    file_size = int(parts[3])
    port = int(parts[5])
    print(f"Downloading file {filename}, size {file_size} bytes, port {port}")

    # Create a new socket to connect to the port allocated by the server
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_address = (server_address[0], port)

    # Open the file to write data
    with open(filename, 'wb') as f:
        start = 0
        while start < file_size:
            # Request a data block (maximum 1000 bytes)
            end = min(start + 999, file_size - 1)
            request = f"FILE {filename} GET START {start} END {end}"
            response = send_and_receive(data_socket, request, data_address)
            if not response:
                print(f"Download of {filename} failed")
                data_socket.close()
                return False

            # Parse the data response
            parts = response.split(maxsplit=7)
            if parts[0] == "FILE" and parts[2] == "OK":
                response_start = int(parts[4])
                response_end = int(parts[6])
                if response_start == start and response_end == end:
                    data = base64.b64decode(parts[7])
                    f.write(data)
                    print("*", end="", flush=True)  # Show the download progress
                    start = end + 1
                else:
                    print(f"Data block error, expected {start}-{end}, received {response_start}-{response_end}")
            else:
                print(f"Invalid response: {response}")
                data_socket.close()
                return False

    # Send a close request
    request = f"FILE {filename} CLOSE"
    response = send_and_receive(data_socket, request, data_address)
    if response and response == f"FILE {filename} CLOSE_OK":
        print(f"\nFile {filename} downloaded successfully")
    else:
        print(f"\nFailed to close file {filename}")

    data_socket.close()
    return True

def main():
    """
    Main function to start the UDP client and download files from the server.

    Steps:
    1. Parse command-line arguments.
    2. Create a UDP socket.
    3. Read the list of files to be downloaded.
    4. Download each file in sequence.
    5. Close the socket after all downloads are completed.
    """
    # Parse command-line arguments
    if len(sys.argv) != 4:
        print("Usage: python3 UDPclient.py <hostname> <port> <files.txt>")
        sys.exit(1)

    hostname = sys.argv[1]
    port = int(sys.argv[2])
    files_list = sys.argv[3]

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (hostname, port)

    # Read the file list
    try:
        with open(files_list, 'r') as f:
            files = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading file list: {e}")
        sys.exit(1)

    # Download each file in sequence
    for filename in files:
        success = download_file(sock, filename, server_address)
        if not success:
            print(f"Skipping file {filename}")

    sock.close()

if __name__ == "__main__":
    main()
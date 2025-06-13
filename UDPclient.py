import socket
import sys
import base64
import time
import os

def send_and_receive(sock, message, server_address, timeout=1, max_retries=5):
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
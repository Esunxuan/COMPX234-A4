# COMPX234-A4
UDP file transfer client and server
Check Client:
Get-FileHash -Algorithm MD5 *pdf,*jpg,*mp4 | Format-Table -Property Hash,Path
Hash                             Path
----                             ----
63BD779267952DEA208A352D153C4F41 F:\作业\系统与网络\COMPX234-A4\Server\test1.pdf
95C1D205CCD51C1595B78F73992BEC9E F:\作业\系统与网络\COMPX234-A4\Server\test2.jpg
3C289230FEFDC127C4C7DEAE2386A288 F:\作业\系统与网络\COMPX234-A4\Server\test3.mp4

Check Server:
Get-FileHash -Algorithm MD5 *pdf,*jpg,*mp4 | Format-Table -Property Hash,Path
Hash                             Path
----                             ----
63BD779267952DEA208A352D153C4F41 F:\作业\系统与网络\COMPX234-A4\Server\test1.pdf
95C1D205CCD51C1595B78F73992BEC9E F:\作业\系统与网络\COMPX234-A4\Server\test2.jpg
3C289230FEFDC127C4C7DEAE2386A288 F:\作业\系统与网络\COMPX234-A4\Server\test3.mp4



### Brief Explanation of Server and Client Implementation

#### Server (UDPserver.py)
- **Functionality**:
  The server operates as a "file dispenser," listening on a specified port (e.g., 51234) for incoming client requests to download files.
- **Implementation**:
  - Utilizes a UDP socket to accept "DOWNLOAD" requests from clients.
  - For each client request, spawns a dedicated thread that:
    - Selects a random high port (range 50000-51000) for data transfer.
    - Validates file existence and readability.
    - Sends initial metadata (file size and data port) to the client.
  - Manages file transfers by:
    - Handling "FILE GET" requests for specific byte ranges (chunks up to 1000 bytes).
    - Encoding file data in Base64 before transmission.
    - Processing "FILE CLOSE" requests to terminate the connection gracefully.
- **Example**:
  When a client requests `test1.pdf`, `test2.jpg`, and `test3.mp4`:
  1. The server assigns a unique data port for each file.
  2. For each chunk requested by the client, the server reads the corresponding bytes from the file, encodes them, and sends them over the data port.
  3. The server tracks the transfer progress and closes the connection after receiving the "FILE CLOSE" command.

#### Client (UDPclient.py)
- **Functionality**:
  The client acts as a "file collector," reading a list of files from `files.txt`, requesting each file from the server, and saving the downloaded data locally.
- **Implementation**:
  - Establishes a UDP socket to send "DOWNLOAD" requests and receive initial file metadata (size and data port).
  - Creates a separate socket for data transfer to the assigned port, where it:
    - Requests file chunks in 1000-byte increments using "FILE GET" commands.
    - Decodes Base64-encoded data and writes it to a local file.
    - Displays download progress as a percentage of total bytes received.
  - Implements reliability features:
    - Timeout and retransmission mechanism (default timeout 2 seconds, 3 retries).
    - Verifies response headers to ensure data integrity.
- **Example**:
  For files listed in `files.txt` (e.g., `test1.pdf`, `test2.jpg`, `test3.mp4`):
  1. The client sends a DOWNLOAD request for each file.
  2. Upon receiving the data port and file size, it requests chunks sequentially.
  3. Each received chunk is decoded, written to the corresponding file, and progress is updated in real-time.
  4. After completing the download, the client sends a "FILE CLOSE" command to finalize the transfer.


# COMPX234-A4
UDP file transfer client and server
Check Client:
Get-FileHash -Algorithm MD5 *pdf,*jpg,*mp4 | Format-Table -Property Hash,Path
Hash                             Path
----                             ----
DC8B51906354A794C7620045A46AEDDE F:\作业\系统与网络\COMPX234-A4\Client\test1.pdf  
178A45157E45C36A69040396BE3FD2A4 F:\作业\系统与网络\COMPX234-A4\Client\test2.jpg  
785C4E992B0286585C9D1CDDB3D82007 F:\作业\系统与网络\COMPX234-A4\Client\test3.mp4 

Check Server:
Get-FileHash -Algorithm MD5 *pdf,*jpg,*mp4 | Format-Table -Property Hash,Path
Hash                             Path
----                             ----
63BD779267952DEA208A352D153C4F41 F:\作业\系统与网络\COMPX234-A4\Server\test1.pdf  
95C1D205CCD51C1595B78F73992BEC9E F:\作业\系统与网络\COMPX234-A4\Server\test2.jpg  
3C289230FEFDC127C4C7DEAE2386A288 F:\作业\系统与网络\COMPX234-A4\Server\test3.mp4  

##### Brief Explanation of Server and Client Implementation

####  Server (UDPserver.py)
- **Functionality**: 
  Server acts like a "librarian," listening on a specified port (e.g., 51234) for client file requests.
- **Implementation**: 
  - Uses a UDP socket to receive "DOWNLOAD" requests.
  - Spawns a new thread for each client request, assigning a random high port (50000-51000) for data transfer.
  - Sends file data in chunks (up to 1000 bytes), encoded in Base64.
  - Handles "FILE GET" requests for data chunks and "FILE CLOSE" to end the connection.
- **Example**: 
  A client requests `test1.pdf`,`test2.jpg`, and `test3.mp4` .The client sends "FILE GET" requests for data chunks, and the server responds with file size and port, then sends data in chunks.

#### Client (UDPclient.py)
- **Functionality**: 
  The client acts like a "reader," reading a list of files from `files.txt`, requesting files from the server, and saving them.
- **Implementation**: 
  - Uses a UDP socket to send "DOWNLOAD" requests, receiving file size and a new port.
  - Creates a new socket to connect to the assigned port, requesting file chunks (up to 1000 bytes).
  -  Decodes Base64 data, writes it to a file, and shows progress (with `*` for each chunk).
  - Supports timeout and retransmission (default timeout 1 second, 5 retries).
- **Example**: 
  The client reads `test1.pdf`,`test2.jpg`, and `test3.mp4`  from `files.txt`, requests the file, receives chunks, saves them, and sends "FILE CLOSE."

---

### Issue with Hash Values Not Matching
- **Problem**: 
   During testing, I found that the MD5 Hash values of the downloaded files (e.g., `Client/test1.pdf`,`test2.jpg`, and `test3.mp4`) and the original server files (e.g., `Server/test1.pdf`,`test2.jpg`, and `test3.mp4`) do not match, indicating incorrect file content.


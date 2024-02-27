# Video-Compressor-Service
Video-Compressor-Service

This project is a client and server service to upload a mp4 file, perform various video processing, and send back to the client. The server program waits on client's requests, and once it received one, it uploads a file to the server and operates ffmpeg command based on the client's request. The clients send requests that were pre-prepared to the server, and then receive the processed file.

### Repositories
* Create a directory for the project and initialize git with command `https://github.com/MarkHash/Video-Compressor-Service.git`

### Environment Set up
* Download and install python and [ffmpeg](https://ffmpeg.org/about.html) if you don’t have it already.

### Deployment
* Run a command `python3 server.py` to start the server.
* Run a command `node client.js` to start the client, and then type a file name to perform ffmpeg command.
* Type a service to perform among "compress", "resolution", "ratio", "audio", and "gif", and choose options (such as height and width) based on the chosen service.
* Based on the requests from the clients, the server sends back with the results of ffmpeg command.

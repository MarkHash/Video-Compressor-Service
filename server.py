import socket, os, time, json, subprocess

# return ffmpeg command to compress mp4 file
def compress(filename, service_option, outputfile):
    if service_option[0] == "low": option = ' -c:v libx264 '
    elif service_option[0] == "medium": option = ' -c:v libx265 '
    else: option = ' -c:v libx265 -b:v 500k '
    return 'ffmpeg -i ' + filename + option + outputfile

# return ffmpeg command to change media resolution
def resolution(filename, option, outputfile):
    return 'ffmpeg -i ' + filename + ' -filter:v scale=' + option[0] + ':' + option[1] + ' -c:a copy ' + outputfile

# return ffmpeg command to
def ratio(filename, option, outputfile):
    return 'ffmpeg -i ' + filename + ' -pix_fmt yuv420p -aspect ' + option[0] + ':' + option[1] + ' ' + outputfile

# return ffmpeg command to output mp3 file from mp4 file
def audio(filename, option, outputfile):
    return 'ffmpeg -i ' + filename + ' -vn ' + outputfile

# return ffmpeg command to create gif file from mp4 file
def gif(filename, option, outputfile):
    return 'ffmpeg -ss ' + option[0] + ' -i ' + filename + ' -to ' + option[1] + ' -r ' + option[2] + ' -vf scale=' + option[3] + ':-1 ' + outputfile

options = {
    "compress": compress,
    "resolution": resolution,
    "ratio": ratio,
    "audio": audio,
    "gif": gif
}

class Socket:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = '0.0.0.0'
        self.server_port = 9001

        self.dpath = 'temp'
        self.output_path = 'output'
        if not os.path.exists(self.dpath):
            os.makedirs(self.dpath)

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    # Biding socket to server address and port, and wait on client's access
    def link(self):
        print(f'starting up on {self.server_address} port {self.server_port}')

        self.sock.bind((self.server_address, self.server_port))
        self.sock.listen(1)

    # 
    def upload(self):
        while True:
            # Obtain client's address
            connection, client_address = self.sock.accept()
            try:
                print(f'connection from {client_address}')
                # Receive file information including service info and option to perform
                header = connection.recv(1024)
                time.sleep(1)
                request = json.loads(header.decode('utf-8'))
                filename = request['filename']
                filename_length = request['filename_length']
                filesize = request['filesize']
                service_type = request['service_type']
                service_option = request['service_option']
                stream_rate = 1400

                print(f'received header from client. filename: {filename}, filename_length: {filename_length}, filesize: {filesize}')
                if filesize == 0:
                    raise Exception('No data to read from client.')
                
                # Create a new file and construct with received information from the client
                with open(os.path.join(self.dpath, filename), 'wb+') as f:
                    while filesize > 0:
                        data = connection.recv(filesize if filesize <= stream_rate else stream_rate)
                        f.write(data)
                        if filesize < 14000: print(f'received {len(data)} bytes. Remaining filesize: {filesize}')
                        filesize -= len(data)
                
                # Define output file name based on the service option
                if service_type == "audio":
                    output_file = "output/output_" + service_type + ".mp3" 
                elif service_type == "gif":
                    output_file = "output/output_" + service_type + ".gif"
                else: 
                    output_file = "output/output_" + service_type + ".mp4"
                
                # Perform ffmpeg command
                cmd = options[service_type](os.path.join(self.dpath, filename), service_option, output_file)
                # print(cmd)
                subprocess.run(cmd.split(' '))

                # Send back a file that was processed by ffmpeg
                with open(output_file, "rb") as f:
                    f.seek(0, os.SEEK_END)
                    filesize = f.tell()
                    f.seek(0,0)

                    if filesize > pow(2, 32):
                        raise Exception('file must be below 2GB.')
                    
                    filename = os.path.basename(f.name)
                    response = {
                        'filename': filename,
                        'filesize': filesize
                        }
                    connection.sendall(json.dumps(response).encode('utf-8'))
                    time.sleep(1)
                    packet_size = 1400
                    data = f.read(packet_size)
                    while data:
                        print('sending...')
                        connection.send(data)
                        data = f.read(packet_size)

            except Exception as e:
                print(f'Error: {str(e)}')
            finally:
                print(f'closing current connection')
                connection.close()
    
def main():
    newSocket = Socket()
    newSocket.link()
    newSocket.upload()

if __name__ == '__main__':
    main()
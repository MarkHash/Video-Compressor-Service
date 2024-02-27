import socket, sys, os,json, time

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # server_address = input("type in the server's address to connect to:")
    server_address = '0.0.0.0'
    server_port = 9001
    packet_size = 1400

    print(f'connecting to {server_address} port {server_port}')

    try:
        sock.connect((server_address, server_port))

    except socket.error as err:
        print(err)
        sys.exit(1)

    try:
        # Obtain filepath, service_type, and service_option from user input
        filepath = input('type in a file name to upload: ')
        service_option = []
        service_type = input('what service would you want for the file? type "compress", "resolution", "ratio", "audio", or "gif": ')
        if service_type == "compress":
            service_option.append('low')
        elif service_type == "resolution":
            service_option.append(input('Please type in the height (ex: 1280)'))
            service_option.append(input('Please type in the width (ex: 720)'))
        elif service_type == "ratio":
            service_option.append(input('Please type in the height (ex: 16)'))
            service_option.append(input('Please type in the width (ex: 9)'))
        elif service_type == "audio":
            service_option.append("")
        elif service_type == "gif":
            service_option.append(input('Input start position (ex. 00:00:20) : '))
            service_option.append(input('Input end position (ex. 10) : '))
            service_option.append(input('Input flame rate (ex. 10) : '))
            service_option.append(input('Input resize (ex. 300) : '))

    # Send the file to the server 
        with open(filepath, 'rb') as f:
            f.seek(0, os.SEEK_END)
            filesize = f.tell()
            f.seek(0,0)

            if filesize > pow(2, 32):
                raise Exception('file must be below 2GB.')
            
            filename = os.path.basename(f.name)
            data_json = {
                'filename': filename,
                'filename_length': len(filename),
                'filesize': filesize,
                'service_type': service_type,
                'service_option': service_option
            }

            # Raise an error if the file is not "mp4" file
            if filename[-4:] != ".mp4":
                raise Exception(f"file:{filename} file must be '.mp4' file")
            
            sock.send(json.dumps(data_json).encode('utf-8'))
            data = f.read(packet_size)
            while data:
                print('sending...')
                sock.send(data)
                data = f.read(packet_size)

        # Receive header information about the processed file from the server
        header = sock.recv(1024)
        print(f'header: {header}')
        time.sleep(1)
        request = json.loads(header.decode('utf-8'))
        filename = request['filename']
        filesize = request['filesize']
        print(request)
        stream_rate = 1400

        print(f'received header from client. filename: {filename}, filesize: {filesize}')
        if filesize == 0:
            raise Exception('No data to read from client.')
        
        # Receive processed file from the server
        with open(filename, 'wb+') as f:
            while filesize > 0:
                data = sock.recv(filesize if filesize <= stream_rate else stream_rate)
                f.write(data)
                if filesize < 14000: print(f'received {len(data)} bytes. Remaining filesize: {filesize}')
                filesize -= len(data)
        sock.send(f'download finished'.encode('utf-8'))
    finally:
        print(f'closing socket')
    sock.close()

if __name__ == '__main__':
    main()
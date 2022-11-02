import sys
from socket import socket
from socket import AF_INET, SOCK_STREAM
import os

def server(port:int):
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('localhost', port))
    serverSocket.listen(1)
    print(serverSocket.getsockname())
    
    
    
    while 1:
        connectionSocket, addr = serverSocket.accept()
        print(f"Request from {addr}")
        data = connectionSocket.recv(1024).decode()
        headers = data.split('\n')
        method = headers[0].split()[0]
        if method == "GET":
            filePath = headers[0].split()[1][1:]
            print(f"Requesting {filePath}")
            success, response = header(filePath)
            connectionSocket.send(response)
            if success:
                fileSend(filePath, connectionSocket)
            connectionSocket.close()
        else:
            connectionSocket.send(methodNotAllowed())

def methodNotAllowed():
    return 'HTTP/1.0 405 Method Not Allowed\n\nError 405 : Method Not Allowed'.encode()

def fileNotFoundResponse():
    return 'HTTP/1.0 404 NOT FOUND\n\nError 404: File Not Found'.encode()

def fileTypeNotSupported():
    return 'HTTP/1.0 501 NOT FOUND\n\nError 501: File Type Not Supported'.encode()

def header(filePath):
    response = 'HTTP/1.0 200 OK \n' 
    fileName = filePath.split("\\")[-1]
    fileExtension = fileName.split(".")[1]

    if fileExtension == "png":
        header = "Content-Type: image/png \n"
        header += "Connection: Closed \n\n"

    elif fileExtension == "html":
        header = "Content-Type: text/html \n"
        header += "Connection: Closed \n\n"
    else:
        return (False, fileTypeNotSupported())
    try:
        f_stat = os.stat(filePath)
    except FileNotFoundError as e:
            return (False, fileNotFoundResponse())
    
    header = f"Content-Length: {f_stat.st_size} \n" + header
    response = response + header
    return (True, response.encode())

def fileSend(filePath, connectSoc):
    try:
            fIn = open(filePath, 'rb')
    except FileNotFoundError as e:
        return
    content = fIn.read(1024)
    while content:
        connectSoc.send(content)
        content = fIn.read(1024)
    fIn.close()
    



    
    


if __name__ == "__main__":
    if(len(sys.argv) != 2):
        raise SystemError("Must include port number") 
    server(int(sys.argv[1]))
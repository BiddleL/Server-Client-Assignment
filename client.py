import sys

from socket import *
import sys


def client():
    serverAddress = (serverHost, serverPort)

    # define a socket for the client side, it would be used to communicate with the server
    clientSocket = socket(AF_INET, SOCK_STREAM)

    # build connection with the server and send message to it
    clientSocket.connect(serverAddress)

    
    while True:
        clientSocket.sendall(message.encode())

        # receive response from the server
        # 1024 is a suggested packet size, you can specify it as 2048 or others
        data = clientSocket.recv(1024)
        receivedMessage = data.decode()

        # parse the message received from server and take corresponding actions
        if receivedMessage == "":
            print("[recv] Message from server is empty!")
        elif receivedMessage == "user credentials request":
            usr = input("> Username: ")
            passwrd = input("> Password: ")
            message
        elif receivedMessage == "download filename":
            print("[recv] You need to provide the file name you want to download")
        else:
            print("[recv] Message makes no sense")
            
        ans = input('\nDo you want to continue(y/n) :')
        if ans == 'y':
            continue
        else:
            break

    # close the socket
    clientSocket.close()

if __name__ == "__main__":
    if(len(sys.argv) != 4):
        print("Usage: python3 client.py server_IP server_port client_udp_port")
        raise SystemError("Usage: python3 client.py server_IP server_port client_udp_port") 
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    client_udp_port = int(sys.argv[3])
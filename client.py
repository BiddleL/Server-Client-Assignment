import sys
import os
from socket import *

import cHelper
from Commands import Commands


def client(serverHost, serverPort, udpPort):
    serverAddress = (serverHost, serverPort)

    # define a socket for the client side, it would be used to communicate with the server
    clientSocket = socket(AF_INET, SOCK_STREAM)

    # build connection with the server and send message to it
    clientSocket.connect(serverAddress)

    outside_active = True
    login_status = False
    user = ""
    while outside_active:
        data = clientSocket.recv(cHelper.BUFFER_SIZE)
        receivedMessage = data.decode()
        message = receivedMessage.splitlines()
        # parse the message received from server and take corresponding actions
        header = message[0]
        if header == "user credentials request":
            login_status = False
            message = str(login(udpPort))
            clientSocket.send(message.encode())
        elif header == "blocked":
            login_status = False
            if message[1] == "wrong password":
                print("> Invalid Password. Your account has been blocked. Please try again later")
            elif message[1] == "login":
                print("> This user is already logged in from another device. Please log out of that device and try again")
            else:
                print("> Your account is blocked due to multiple authentication failures. Please try again later")
            active = False
            break
        elif header == "wrong password":
            login_status = False
            print("> Invalid Password. Please try again")
            message = login(udpPort)
            clientSocket.send(message.encode())
        elif header == "login success" or login_status:
            if header == "login success":
                login_status = True
                outside_active = False
                user = message[1] 
                print("> Welcome!")
    
    while login_status:
        usrCommand = input("> Enter one of the following commands (EDG, UED, SCS, DTE, AED, OUT, UVF):\n> ")
        commands = usrCommand.split(" ")
        command = -1
        try:
            command = Commands[commands[0]].value
        except KeyError:
            print("> Error. Invalid command!")
        # client command behaviour
        if command > 0 and command <= 7:
            # EDG
            if command == 1: 
                try:
                    fileID = int(commands[1])
                    size = int(commands[2])
                    cHelper.edg(fileID, size, user)
                except IndexError:
                    print("> EDG command requires fileID and dataAmount as arguments")
                
                
            # UED
            elif command == 2:
                flag = True
                message = None
                try:
                    fileID = commands[1]
                    fileIDi = int(fileID)
                    message = "UED\n\n"
                    clientSocket.sendall(message.encode())
                    data = clientSocket.recv(cHelper.BUFFER_SIZE)
                    header = data.decode().splitlines()[0]
                    message = cHelper.ued(fileID, user)
                except IndexError:
                    flag = False
                    print("> UED command requires fileID as an argument\n")
                except ValueError:
                    flag = False
                    print("> UED command requires fileID as an integer\n")
                if message != None and flag:
                    clientSocket.sendall(message.encode())
                    data = clientSocket.recv(cHelper.BUFFER_SIZE)
                    message = data.decode().splitlines()
                    header = message[0]
                    if header == "UED":
                        if "success" in message:
                            if "exist" in message:
                                print(f"> Data file with ID of {fileID} has been replaced on server\n")
                            else:
                                print(f"> Data file with ID of {fileID} has been uploaded to server\n")
                else:
                    message = "UED\nfail\n\n"
                    clientSocket.sendall(message.encode())
            # SCS
            elif command == 3:
                message = ""
            # DTE
            elif command == 4:
                try:
                    fileID = commands[1]
                    message = cHelper.dteS(fileID)
                except IndexError:
                    print("> DTE command requires fileID as an argument\n")
                
                clientSocket.sendall(message.encode())
                data = clientSocket.recv(cHelper.BUFFER_SIZE)
                cHelper.dteR(data)

            # AED
            elif command == 5:
                message = "AED\n\n"
                clientSocket.sendall(message.encode())
                data = cHelper.recvall(clientSocket).decode()
                response = data.split("\n")
                if response[1] == "None":
                    print("> This client is the only user")
                else:
                    print("> Current active users: ")
                    for l in response[1:]:
                        fields = l.split("; ")
                        name = fields[0]
                        time = fields[1]
                        ip = fields[2]
                        port = fields[3]
                        
                        print(f"{name} active since {time} on {ip} with UDP port {port}\n")


            # OUT
            elif command == 6:
                message = "OUT\n\n"
                clientSocket.sendall(message.encode())
                data = clientSocket.recv(cHelper.BUFFER_SIZE)
                receivedMessage = data.decode()
                login_status = False
                if message == receivedMessage:
                    # OUT confirmed
                    print(f"\n> Bye, {user}!\n")
                    break
            # UVF
            elif command == 7:
                message = ""
        
    # close the socket
    clientSocket.close()

def login(port):
    print('\n')
    usr = input("> Username: ")
    passwrd = input("> Password: ")
    message = f"login\nusr:{usr}\npassword:{passwrd}\nudp:{port}\n"
    return message


if __name__ == "__main__":
    if(len(sys.argv) != 4):
        print("Usage: python3 client.py server_IP server_port client_udp_port")
        raise SystemError("Usage: python3 client.py server_IP server_port client_udp_port") 
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    client_udp_port = int(sys.argv[3])
    client(server_ip, server_port, client_udp_port)
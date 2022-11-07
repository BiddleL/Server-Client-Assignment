import sys
from socket import *


from helper import Commands


def client(serverHost, serverPort, udpPort):
    serverAddress = (serverHost, serverPort)

    # define a socket for the client side, it would be used to communicate with the server
    clientSocket = socket(AF_INET, SOCK_STREAM)

    # build connection with the server and send message to it
    clientSocket.connect(serverAddress)

    active = True
    login_status = False
    user = ""
    while active:
        data = clientSocket.recv(2048)
        receivedMessage = data.decode()
        message = receivedMessage.splitlines()
        print(f"Incoming:{message}")
        # parse the message received from server and take corresponding actions
        header = message[0]
        if header == "user credentials request":
            login_status = False
            message = str(login(udpPort))
            clientSocket.send(message.encode())
        elif header == "blocked":
            login_status = False
            if message[1] == "wrong password":
                print("> Invalid Password. Your account has been blocked. Please try again later\n")
            elif message[1] == "login":
                print("> This user is already logged in from another device. Please log out of that device and try again\n")
            else:
                print("> Your account is blocked due to multiple authentication failures. Please try again later\n")
            active = False
            break
        elif header == "wrong password":
            login_status = False
            print("> Invalid Password. Please try again\n")
            message = login(udpPort)
            clientSocket.send(message.encode())
        elif header == "login success" or login_status:
            if header == "login success":
                login_status = True
                user = message[1] 
                print("> Welcome!\n")
            usrCommand = input("> Enter one of the following commands (EDG, UED, SCS, DTE, AED, OUT, UVF):\n")
            commands = usrCommand.split(" ")
            command = -1
            try:
                command = Commands[commands[0]].value
            except KeyError:
                print("> Error. Invalid command!\n")
            # client command behaviour
            if command > 0 and command <= 7:
                # EDG
                if command == 1: 
                    message = ""
                # UED
                elif command == 2:
                    message = ""
                # SCS
                elif command == 3:
                    message = ""
                # DTE
                elif command == 4:
                    message = ""
                # AED
                elif command == 5:
                    message = ""
                # OUT
                elif command == 6:
                    active = False
                    message = "OUT\n\n"
                    clientSocket.sendall(message.encode())
                    data = clientSocket.recv(2048)
                    receivedMessage = data.decode()
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
    print('\n')
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
import sys

from socket import *
import sys




def client(serverHost, serverPort):
    serverAddress = (serverHost, serverPort)

    # define a socket for the client side, it would be used to communicate with the server
    clientSocket = socket(AF_INET, SOCK_STREAM)

    # build connection with the server and send message to it
    clientSocket.connect(serverAddress)

    active = True
    while active:


        # receive response from the server
        # 1024 is a suggested packet size, you can specify it as 2048 or others
        data = clientSocket.recv(2048)
        receivedMessage = data.decode()
        message = receivedMessage.splitlines()
        # parse the message received from server and take corresponding actions
        if receivedMessage[0] == "user credentials request":
            usr = input("> Username: ")
            passwrd = input("> Password: ")
            message = f"login\nusr:{usr}\npassword:{passwrd}\n\n"
        if receivedMessage[0] == "blocked":
            if receivedMessage[1] == "wrong password":
                print("Invalid Password. Your account has been blocked. Please try again later\n")
            else:
                print("Your account is blocked due to multiple authentication failures. Please try again later\n")
            active = False
            break
                
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
    client
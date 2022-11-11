import os
from threading import Thread
import sys, select
from socket import *
from datetime import datetime

import sHelper
from Commands import Commands

usersBlocked = dict() # key = username, value = blocked time
usrActiveList = [] # list of active usernames 
numSuccessful = 0
clients = []

def TCPserver(ip, port, attempts):
    serverHost = ip
    serverAddress = (serverHost, port)
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(serverAddress)
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(serverAddress)
    print(f"Server started {serverHost}:{port}")
    # console = Console()
    # console.start()
    while True:
        serverSocket.listen()
        clientSockt, clientAddress = serverSocket.accept()
        clientThread = ClientThread(clientAddress, clientSockt, attempts)
        global clients
        clients.append(clientThread)
        clientThread.start()


def UDPserver():
    return False

class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket, m_num_attempts):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = True
        self.MAX_ATTEMPTS = m_num_attempts
        self.loginStatus = False
        self.numAttempts = 0
        self.currUser = ""
        self.joinTime = None
        self.udpSocket = -1
        
    
    # Single server thread
    def run(self):
        print(f"Starting client thread on {self.clientAddress}")
        message = "user credentials request\n\n"
        self.clientSocket.send(message.encode())
        while self.clientAlive:
            # use recv() to receive message from the client
            data = self.clientSocket.recv(sHelper.BUFFER_SIZE)
            if data == b'':
                self.clientAlive = False
                break
            message_decoded = data.decode()
            message = message_decoded.splitlines()
            
            header = message[0]
            try:
                command = Commands[header].value
                command_flag = True
            except KeyError:
                command_flag = False
            if command_flag:
                if command > 0 and command <= 7:
                    # EDG
                    if command == 1: 
                        message = ""
                    # UED
                    elif command == 2:
                        if message[1] != "fail":
                            response = "UED\n\n"
                            self.clientSocket.sendall(response.encode())
                            print(f"> Edge device {self.currUser} issued UED command")
                            response = sHelper.uedR(self)
                            if response != None:
                                self.clientSocket.sendall(response.encode())

                    # SCS
                    elif command == 3:
                        # try:
                            fileID = int(message[1])
                            operation = message[2]
                            response = sHelper.scs(fileID, usr, operation)
                            self.clientSocket.sendall(response.encode())
                        # except ValueError:
                        #     print("> SCS error")
                        #     self.clientSocket.sendall("SCS\npacket-error\n\n".encode())

                    # DTE
                    elif command == 4:
                        response = sHelper.dteDelete(message, self.currUser) 
                        self.clientSocket.sendall(response.encode())
                    # AED
                    elif command == 5:
                        response = sHelper.aed(self)
                        self.clientSocket.sendall(response.encode())

                    # OUT
                    elif command == 6:
                        self.clientAlive = False
                        response = "OUT\n\n"
                        self.clientSocket.sendall(response.encode())
                        break
                    # UVF
                    elif command == 7:
                        message = ""
                        
            else:
                if header == 'login':
                    usrS = message[1].split(':')
                    passwrdS = message[2].split(':')
                    portS = message[3].split(':')
                    if usrS[0] == "usr" and passwrdS[0] == "password" and portS[0] == "udp":
                        usr = usrS[1]
                        passwrd = passwrdS[1]
                        port = portS[1]
                        message = self.process_login(usr, passwrd, port)
                        self.clientSocket.send(message.encode())
        if self.loginStatus:
            self.logout()
        print(f"Closing client thread on {self.clientAddress}")
    
    # Processing authentication
    def process_login(self, usr, passwrd, port):
        login_status = sHelper.usrLogin(usr, passwrd)
        global usersBlocked
        blockedStatus = sHelper.usrBlocked(usr, usersBlocked)
        global usrActiveList
        alreadyLogged = sHelper.usrAlreadyLoggedIn(usr, usrActiveList)
        if blockedStatus:
            message = "blocked\n\n"
            return message
        elif not login_status:
            message = "wrong password\n"
            self.numAttempts += 1
            if(self.numAttempts >= self.MAX_ATTEMPTS):
                usersBlocked = sHelper.blockUser(usr, usersBlocked)
                message = "blocked\n" + message
            message += '\n'
            return message
        elif alreadyLogged:
            message = "blocked\nlogin\n\n"
            return message
        elif login_status and not blockedStatus and not alreadyLogged:
            self.loginStatus = True
            self.currUser = usr
            self.joinTime = datetime.now()
            self.udpSocket = port

            usrActiveList.append(usr)
            
            global numSuccessful 
            numSuccessful += 1
            
            sHelper.writeActiveLog(self)
            message = f"login success\n{self.currUser}\n\n"
            return message
    
    # Perform cleanup and log client out
    def logout(self):
        global usrActiveList
        usrActiveList.remove(self.currUser)
        sHelper.removeActiveLog(self)
        self.clientSocket.close()
        self.loginStatus = False
        global clients
        clients.remove(self)
        print(f"\n{self.currUser} exited the edge network\n")

# class Console(Thread):
#     def __init__(self):
#         Thread.__init__(self)
#     def run(self):
#         i = " "
#         while i != "":
#             if i == "clear":
#                 global clients
#                 for c in clients:
#                     c.logout()
#                     c.stop()






if __name__ == "__main__":
        
    if(len(sys.argv) != 4):
        print("Usage: python3 server.py server_ip server_port number_of_consecutive_failed_attempts")
    ip = str(sys.argv[1])
    tcp_port = int(sys.argv[2])
    num_attempts = int(sys.argv[3])
    try:
        os.remove("edge-device-log.txt")
        os.remove("upload-log.txt")
        os.remove("deletion-log.txt")

    except:
        True
    TCPserver(ip, tcp_port, num_attempts)
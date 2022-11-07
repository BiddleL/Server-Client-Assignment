import os
from threading import Thread
import sys, select
from socket import *
from datetime import datetime

from helper import loadCredential, usrBlocked, usrLogin, blockUser, usrAlreadyLoggedIn
from helper import Commands

usersBlocked = dict() # key = username, value = blocked time
usrActiveList = [] # list of active usernames 
numSuccessful = 0

def TCPserver(port, attempts):
    serverHost = "localhost"
    serverAddress = (serverHost, port)
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(serverAddress)
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(serverAddress)
    print(f"Server started {serverHost}:{port}")
    while True:
        serverSocket.listen()
        clientSockt, clientAddress = serverSocket.accept()
        clientThread = ClientThread(clientAddress, clientSockt, attempts)
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
        message = self.cred_request()
        self.clientSocket.send(message.encode())
        while self.clientAlive:
            # use recv() to receive message from the client
            data = self.clientSocket.recv(2048)
            if data == b'':
                self.clientAlive = False
                break
            message = data.decode()
            message_decoded = message.splitlines()
            
            header = message_decoded[0]
            try:
                command = Commands[header].value
                command_flag = True
            except KeyError:
                command_flag = False
            print(f"Incoming: {message_decoded}")
            if command_flag:
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
                        self.clientAlive = False
                        message = "OUT\n\n"
                        self.clientSocket.sendall(message.encode())
                        break
                    # UVF
                    elif command == 7:
                        message = ""
                        
            else:
                if header == 'login':
                    usrS = message_decoded[1].split(':')
                    passwrdS = message_decoded[2].split(':')
                    portS = message_decoded[3].split(':')
                    if usrS[0] == "usr" and passwrdS[0] == "password" and portS[0] == "udp":
                        usr = usrS[1]
                        passwrd = passwrdS[1]
                        port = portS[1]
                        message = self.process_login(usr, passwrd, port)
                        self.clientSocket.send(message.encode())
        if self.loginStatus:
            self.logout()
        print(f"Closing client thread on {self.clientAddress}")
        
            
    # Request credentials from client
    def cred_request(self):
        message = "user credentials request\n\n"
        return message 
    # Write client info to log after successful join
    def write_active_log(self):
        i = 0
        try:
            with open("edge-device-log.txt", 'r') as f:
                file = f.readlines()
                i = len(file)
                f.close()
        except IOError:
            i = 1

        line = ""
        now = self.joinTime.strftime("%d %B %Y %H:%M:%S")
        line += now + "; "
        line += f"{self.currUser}; "
        line += f"{self.clientAddress}; "
        line += f"{self.udpSocket}\n"
        line = f"{i} " + line
        
        try:
            with open("edge-device-log.txt", 'a+') as f:
                f.write(line)
                f.close()
        except IOError:
            raise IOError("Error with loading edge log file")
    
    # Processing authentication
    def process_login(self, usr, passwrd, port):
        login_status = usrLogin(usr, passwrd)
        global usersBlocked
        blockedStatus = usrBlocked(usr, usersBlocked)
        global usrActiveList
        alreadyLogged = usrAlreadyLoggedIn(usr, usrActiveList)
        if blockedStatus:
            message = "blocked\n\n"
            return message
        elif not login_status:
            message = "wrong password\n"
            self.numAttempts += 1
            if(self.numAttempts >= self.MAX_ATTEMPTS):
                usersBlocked = blockUser(usr, usersBlocked)
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
            
            self.write_active_log()
            message = f"login success\n{self.currUser}\n\n"
            return message
    
    def remove_active_log(self):
        newfile = ""
        try:
            with open("edge-device-log.txt", 'r') as f:
                file = f.readlines()
                flag = False
                l = len(file)
                if l > 1:
                    for i in range(l):
                        s = file[i].split("; ")
                        username = s[2]
                        if username == self.currUser and flag == False:
                            index = i + 1
                            flag = True
                        elif flag:
                            s[0] = str(index)
                            index += 1
                            newfile += "; ".join(s) + '\n'
                        else:
                            newfile += file[i] + '\n'
                f.close()      
        except IOError:
            raise IOError("Error with loading edge log file")
        os.remove("edge-device-log.txt")
        try:
            with open("edge-device-log.txt", 'w') as f:
                f.write(newfile)
                f.close()
        except IOError:
            raise IOError("Error with creating edge log file")

    def logout(self):
        global usrActiveList
        usrActiveList.remove(self.currUser)
        self.remove_active_log()
        self.clientSocket.close()
        self.loginStatus = False
        print(f"\n{self.currUser} exited the edge network\n")



if __name__ == "__main__":
        
    if(len(sys.argv) != 3):
        print("Usage: python3 server.py server_port number_of_consecutive_failed_attempts")
        raise SystemError("Usage: python3 server.py server_port number_of_consecutive_failed_attempts") 
    tcp_port = int(sys.argv[1])
    num_attempts = int(sys.argv[2])
    try:
        os.remove("edge-device-log.txt")
    except:
        True
    TCPserver(tcp_port, num_attempts)
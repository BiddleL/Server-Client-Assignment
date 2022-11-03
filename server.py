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
    return True

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
    
    def run(self):
        message = ''
        self.cred_request()

        while self.clientAlive:
            # use recv() to receive message from the client
            data = self.clientSocket.recv(2048)
            message = data.decode()
            message_decoded = message.split('\n')
            header = message[0]
            try:
                command = Commands[header].value()
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
                        if self.loginStatus:
                            usrActiveList.remove(self.currUser)
                            self.loginStatus = False
                        self.clientAlive = False
                        break
                    # UVF
                    elif command == 7:
                        message = ""
                        
            else:
                if header == 'login':
                    usrS = message[1].split(':')
                    passwrdS = message[2].split(':')
                    if usrS[0] == "usr" and passwrdS[0] == "password":
                        usr = usrS[1]
                        passwrd = passwrdS[1]
                        self.process_login(usr, passwrd)
            
            
            


    def cred_request(self):
        message = "user credentials request\n\n"
        self.clientSocket.send(message.encode())

    def process_login(self, usr, passwrd):
        login_status = usrLogin(usr, passwrd)
        blockedStatus = usrBlocked(usr, usersBlocked)
        alreadyLogged = usrAlreadyLoggedIn(usr, usrActiveList)
        if blockedStatus:
            message = "blocked\n\n"
            self.clientSocket.send(message.encode)
        elif not login_status:
            message = "wrong password\n"
            self.num_attempts += 1
            if(self.numAttempts >= self.MAX_ATTEMPTS):
                usersBlocked = blockUser(usr, usersBlocked)
                message = "blocked\n" + message
            message += '\n'
            self.clientSocket.send(message.encode)
        elif alreadyLogged:
            message = "blocked\nlogin\n\n"
            self.clientSocket.send(message.encode)
        elif login_status and not blockedStatus and not alreadyLogged:
            self.loginStatus = True
            usrActiveList.append(usr)
            self.currUser = usr
            self.joinTime = datetime.now()
            message = "login success"
            numSuccessful += 1
            write_log(numSuccessful)
            self.clientSocket.send(message.encode)
            

    def write_log(self, i):
        line = f"{i} "
        now = self.joinTime.strftime("%d %B %Y %H:%M:%S")
        line += now + "; "
        line += f"{self.currUser}; "
        line += f"{self.clientAddress}; "
        line += f"{self.udpSocket}\n"
        
        try:
            with open("edge-device-log.txt", 'r') as f:
                f.write(line)
                f.close()
        except IOError:
            raise IOError("Error with loading edge log file")





        


            

if __name__ == "__main__":
    if(len(sys.argv) != 3):
        print("Usage: python3 server.py server_port number_of_consecutive_failed_attempts")
        raise SystemError("Usage: python3 server.py server_port number_of_consecutive_failed_attempts") 
    tcp_port = int(sys.argv[1])
    num_attempts = int(sys.argv[2])
    
    TCPserver(tcp_port, num_attempts)
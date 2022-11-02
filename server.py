from threading import Thread
import sys, select
from socket import *

from helper import loadCredential, usrBlocked, usrLogin, blockUser

usersBlocked = dict() # key = username, value = blocked time
usrActiveList = [] # list of active usernames 

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
        self.max_num_attempts = m_num_attempts
        self.login_status = False
        self.num_attempts = 0
    
    def run(self):
        message = ''
        self.cred_request()

        while self.clientAlive:
            # use recv() to receive message from the client
            data = self.clientSocket.recv(2048)
            message = data.decode()
            message_decoded = message.split('\n')

            # handle message from the client
            if message[0] == 'login':
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
        loginStatus = usrLogin(usr, passwrd)
        blockedStatus = usrBlocked(usr, usersBlocked)
        if blockedStatus:
            message = "blocked\n\n"
            self.clientSocket.send(message.encode)
        elif not loginStatus:
            message = "wrong password\n"
            self.num_attempts += 1
            if(self.num_attempts >= self.max_num_attempts):
                usersBlocked = blockUser(usr, usersBlocked)
                message = "blocked\n" + message
            message += '\n'
            self.clientSocket.send(message.encode)
        


            

if __name__ == "__main__":
    if(len(sys.argv) != 3):
        print("Usage: python3 server.py server_port number_of_consecutive_failed_attempts")
        raise SystemError("Usage: python3 server.py server_port number_of_consecutive_failed_attempts") 
    tcp_port = int(sys.argv[1])
    num_attempts = int(sys.argv[2])
    
    TCPserver(tcp_port, num_attempts)
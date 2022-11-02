from threading import Thread
import sys, select
from socket import *

from helper import loadCredential



class ClientThread(Thread):
    def __init__(self, clientAddress, clientSocket, num_attempts):
        Thread.__init__(self)
        self.clientAddress = clientAddress
        self.clientSocket = clientSocket
        self.clientAlive = True
        self.num_attempts = num_attempts
        self.login_status = False
        self.credentials = loadCredential()

    def run(self):
        message = ''
        self.cred_request()

        while self.clientAlive:
            # use recv() to receive message from the client
            data = self.clientSocket.recv(1024)
            message = data.decode()
            
            # if the message from client is empty, the client would be off-line then set the client as offline (alive=Flase)
            if message == '':
                self.clientAlive = False
                print("===== the user disconnected - ", self.clientAddress)
                break
            
            # handle message from the client
            if message == 'login':
                print("[recv] New login request")
                self.process_login()
            elif message == 'download':
                print("[recv] Download request")
                message = 'download filename'
                print("[send] " + message)
                self.clientSocket.send(message.encode())
            else:
                print("[recv] " + message)
                print("[send] Cannot understand this message")
                message = 'Cannot understand this message'
                self.clientSocket.send(message.encode())
    

    def cred_request(self):
        message = 'user credentials request'
        self.clientSocket.send(message.encode())

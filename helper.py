from datetime import datetime
from enum import Enum
import os

def loadCredential():
    try:
        with open("credentials.txt", 'r') as f:
            lines = f.readlines()
            f.close()
    except IOError:
        raise IOError("Error with loading credentials file")
    
    credentials = dict()

    for i in lines:
        i_split = i.split(" ")
        if len(i_split) == 2:
            usr = i_split[0]
            passwrd = i_split[1]
            credentials[usr] = passwrd
    if len(credentials) == 0:
        raise ImportError("No entries in credentials file")
    return credentials

# Return True if usr is blocked
# False if not blocked
def usrBlocked(usr, blockedList):
    currTime = datetime.now()
    if usr in blockedList:
        usrTime = blockedList[usr]
        diff = currTime - usrTime
        if abs(diff.seconds) > 10:
            blockedList.pop(usr)
            return False 
        else:
            return True
    return False

def usrLogin(usr, passwrd):
    creds = loadCredential()
    if usr in creds:
        if creds[usr] == passwrd:
            return True
        
    return False

def blockUser(usr, blockedList):
    blockedList[usr] = datetime.now()
    return blockedList

def usrAlreadyLoggedIn(usr, activeList):
    if usr in activeList:
        return True
    else: 
        return False

def deleteActiveLog(usr):
    try:
        with open("edge-device-log.txt", 'w') as f:
            lines = f.readlines()
            f.close()
    except IOError:
        raise IOError("Error with loading active edge log file")

    for i in lines:
        lineS = i.split("; ")
        if lineS[2] == usr:
            lines.remove(i)

    prev = 0
    for i in range(len(lines)):
        lineS = lines[i].split("; ")
        index = lineS[0]
        if index != prev + 1:
            lines[i] = f"{prev+1};" + lines[len(index)+1:]
        prev += 1
    os.remove("edge-device-log.txt")
    try:
        with open("edge-device-log.txt", 'a') as f:
            f.writelines(lines[:-1])
            f.close()
    except IOError:
        raise IOError("Error with loading active edge log file")
    


class Commands(Enum):
    EDG = 1
    UED = 2
    SCS = 3
    DTE = 4
    AED = 5
    OUT = 6
    UVF = 7

from datetime import datetime
import os
from statistics import mean

BUFFER_SIZE = 2048

from server import ClientThread

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
            passwrd = i_split[1][:].split('\n')[0]
            credentials[usr] = passwrd
    if len(credentials) == 0:
        raise ImportError("No entries in credentials file")
    return credentials

def recvall(thread: ClientThread):
    data = b''
    while True:
        part = thread.clientSocket.recv(BUFFER_SIZE)
        data += part
        if len(part) < BUFFER_SIZE:
            # either 0 or end of data
            break
    return data

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

def writeActiveLog(thread: ClientThread):
    i = 0
    try:
        with open("edge-device-log.txt", 'r') as f:
            file = f.readlines()
            i = len(file)
            f.close()
    except IOError:
        i = 1

    line = ""
    now = thread.joinTime.strftime("%d %B %Y %H:%M:%S")
    line += now + "; "
    line += f"{thread.currUser}; "
    line += f"{thread.clientAddress}; "
    line += f"{thread.udpSocket}\n"
    line = f"{i}; " + line
    
    try:
        with open("edge-device-log.txt", 'a+') as f:
            f.write(line)
            f.close()
    except IOError:
        raise IOError("Error with loading edge log file")

def removeActiveLog(thread: ClientThread):
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
                        if username == thread.currUser and flag == False:
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

def uploadLog(usr, id, amount):
    try:
        with open("upload-log.txt", 'a+') as f:
            time = datetime.now().strftime("%d %B %Y %H:%M:%S")
            log = f"{usr}; {time}; {id}; {amount}\n"
            f.write(log)
    except IOError:
            print(f"> Error writing {usr}-{id}.txt to upload log\n")

def dteLog(usr, id, amount):
    try:
        with open("deletion-log.txt", 'a+') as f:
            time = datetime.now().strftime("%d %B %Y %H:%M:%S")
            log = f"{usr}; {time}; {id}; {amount}\n"
            f.write(log)
    except IOError:
            print(f"> Error writing {usr}-{id}.txt to deletion log\n")

def dteDelete(message, user):
    try:
        fileID = message[1]
        fileIDi = int(fileID)
    except KeyError:
        print(f"> Incorrect DTE request from {user} without fileID.\n")
        return ""
    except ValueError:
        print(f"> Incorrect DTE request from {user} as fileID isn't an integer.\n")
        return ""

    message = "DTE\n"
    print(f"> Edge device {user} issued DTE command, the file ID is {fileID}\n")
    filename = f"{user}-{fileID}.txt"
    if os.path.exists(filename):
        length = 0
        with open(filename, 'r') as f:
            lines = f.readlines()
            for l in lines:
                length += 1
            f.close()
        try:
            os.remove(filename)
            message += f"success\n{fileID}\n\n"
            print(f"> The file with ID of {fileID} from edge device {user} has been deleted, deletion log file has been updated\n")
            dteLog(user, fileID, length)
        except Exception:
            message += f"error\n{fileID}\n\n"
            
    else:
        message += f"non-exist\n{fileID}\n\n"
    
    return message

def uedR(thread: ClientThread):
    message = recvall(thread).decode()
    header = message.splitlines()
    response = ""
    existFlag = False
    if header[0] == "UED":
        if header[1] != "fail":
            print(f"> A data file is received from edge device {thread.currUser}")
            fileID = header[1]
            usr = thread.currUser
            filename = f"{usr}-{fileID}.txt"
            if os.path.exists(filename):
                os.remove(filename)
                existFlag = True
            sFlag = False
            success = False
            length = 0
            try:
                with open(filename, 'w') as f:
                    for l in header:
                        if sFlag and l != "END" and l != '':
                            s = f"{l}\n"
                            f.write(s)
                            length += 1
                        
                        if l == "START":
                            sFlag = True
                        if l == "END":
                            break
                        
                    f.close()
                    success = True
            except IOError:
                print(f"> Error creating file: {filename}\n")
                response = "error"
        else:
            success = False
            response = None
            

        if success:
            response = "UED\nsuccess\n"
            if existFlag:
                response += "exist\n"
            response += "\n"
            uploadLog(thread.currUser, fileID, length)
            print(f"> The file with ID of {fileID} has been received from {thread.currUser}, upload-log.txt has been updated")
        return response
  
def readActiveLog(currentUser):
    try:
        with open("edge-device-log.txt", 'r') as f:
            file = f.readlines()
            i = len(file)
            f.close()
    except:
        raise IOError("Error with loading edge log file")
    
    devices = []
    for d in file:
        l = d.split("; ")
        entry = dict()
        entry["time"] = l[1]
        entry["usr"] = l[2]
        entry["ip"] = l[3]
        entry["udp-port"] = l[4]
        if entry["usr"] != currentUser:
            devices.append(entry)
    return devices
        
def aed(thread: ClientThread):
    usrs = readActiveLog(thread.currUser)
    response = "AED\n"
    print(f"> Edge device {thread.currUser} issued AED command\n")
    message = ""
    reponse = ""
    for u in usrs:
        name = u["usr"]
        ip = u["ip"]
        time = u["time"]
        port = u["udp-port"]
        response += f"{name}; {time}; {ip}; {port}\n"
        
        message += f"{name}, active since {time} on {ip} with UDP port: {port}\n"
    if len(usrs) <= 0:
        response = "AED\nNone\n\n"
    else:
        print(f"> Return message: {message}")
        response += '\n'
    return response 

def readData(fileName):
    data = []
    with open(fileName, 'r') as f:
        for l in f.readlines():
            data.append(float(l))
    return data

def scs(id, usr, oper):
    filename = f"{usr}-{id}.txt"
    if os.path.exists(filename):
        data = readData(filename)
        response = f"SCS\n{oper}\n"
        if oper == "MAX":
            response += f"{max(data)}\n\n"
        elif oper == "MIN":
            response += f"{min(data)}\n\n"
        elif oper == "SUM":
            response += f"{sum(data)}\n\n"
        elif oper == "AVERAGE":
            response += f"{mean(data)}\n\n"
        else:
            response += "error\n\n"
        return response
    else:
        return "SCS\nno-exist\n\n"


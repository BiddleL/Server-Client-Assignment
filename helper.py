from datetime import datetime

def loadCredential():
    try:
        with open("credentials.txt", 'r') as f:
            lines = f.readlines()
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
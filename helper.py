
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


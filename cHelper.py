import os

BUFFER_SIZE = 2048

def edg(fileID, size, user):

    try:
        fileIDi = int(fileID)
        sizeI = int(size)
    except ValueError:
        print("> The fileID or dataAmount are not integers, you need to specify the parameter as integers\n")

    print(f"> The edge device is generating {size} data samples...")

    filename = f"{user}-{fileIDi}.txt" 
    if os.path.exists(filename):
        os.remove(filename)
    
    try:
        with open(filename, 'w+') as f:
            for i in range(1, size+1):
                f.write(f"{i}\n")
            f.close()
        print(f"> Data generation done, {size} data samples have been generated and stored in file {filename}\n")
        
    except IOError:
        raise IOError("Error with creating data file")

def dteS(fileID):
    try:
        fileIDi = int(fileID)
    except ValueError:
        print("> The fileID is not an integer, you need to specify the parameter as integers\n")
    
    message = f"DTE\n{fileIDi}\n\n"
    return message

def dteR(data):
    message = data.decode().splitlines()
    header = message[0]
    if header == "DTE":
        body = message[1]
        if body == "non-exist":
            print(f"> The file with ID of {message[2]} doesn't exist.\n")
        elif body == "success":
            print(f"> The file with ID of {message[2]} has been successfully been deleted\n")
        elif body == "error":
            print(f"> Unknown error when deleting file {message[2]}, please try again.\n")
    else:
        print("> DTE Packet in incorrect format.\n")

def ued(fileID, user):
    filename = f"{user}-{fileID}.txt"
    message = ""
    if os.path.exists(filename):
        message = f"UED\n{fileID}\nSTART\n"
        try:
            with open(filename, 'r') as f:
                while True:
                    buffer = 1024 
                    fIn = f.read(buffer)
                    if fIn == 0:
                        break
                    message += fIn
                message += "END\n\n"
        except:
            print("> UED: File loading error\n")
            message = None
    else:
        print(f"> File {filename} cannot be uploaded as it doesn't exist.\n")
        message = None
    
    return message

def uedR(data):
    message = data.decode().splitlines()
    



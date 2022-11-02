import sys

def TCPserver(port, attempts):
    return True

def UDPserver():
    return False

if __name__ == "__main__":
    if(len(sys.argv) != 3):
        print("Usage: python3 server.py server_port number_of_consecutive_failed_attempts")
        raise SystemError("Usage: python3 server.py server_port number_of_consecutive_failed_attempts") 
    tcp_port = int(sys.argv[1])
    num_attempts = int(sys.argv[2])
    
    TCPserver(tcp_port, num_attempts)
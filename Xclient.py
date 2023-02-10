# import requests
# import urllib3
# urllib3.disable_warnings()
# res = requests.get('https://localhost:443', verify='./certificate.pem')
# print(res)

import socket
import ssl
from PrettyLogger import logger_config
import Constants
import threading


from PrettyLogger import logger_config
log = logger_config("webserver")

'''

with socket.create_connection((hostname, 443)) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        ssock.sendall("GET / HTTP/1.1\r\nHost: localhost\r\n\r\n".encode("ASCII"))
        buffer = ssock.recv(1024)
        print(buffer.decode("UTF-8"))  
'''

def establish_HTTPS_connection() -> socket.socket:
    hostname = 'localhost'
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations("./keys/certificate.pem")

    '''
    # Use two lines below instead of line above if you don't want to check self-signed certificate 
    context.verify_mode = ssl.CERT_NONE 
    context.check_hostname = False
    '''

    raw_sock = socket.create_connection((hostname, 443))
    https_sock = context.wrap_socket(raw_sock, server_hostname = Constants.X_SERVER_DOMAIN_NAME)
    
    return https_sock

def client_handler(https_socket: socket.socket):
    UDP_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDP_server_socket.bind(("localhost", Constants.XCLIENT_UDP_PORT))
    
    while True:
        bytes_address_pair = UDP_server_socket.recvfrom(Constants.BUFFER_SIZE)
        message = bytes_address_pair[0].decode("ascii")
        https_message = f"PUT / HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/zip\r\nContent-Length: {len(message)}\r\n\r\n{message}"
        https_socket.sendall(https_message.encode("ascii"))


def xserver_handler(https_socket: socket.socket):
    pass

if __name__ == "__main__":
    https_socket = establish_HTTPS_connection()

    # This thread listens on XCLIENT_UDP_PORT and forwards incomming packets to XSERVER after adding header
    client_handler_thread = threading.Thread(target=client_handler, args=(https_socket, ))
    client_handler_thread.start()

    # This thread reads from HTTPS socket and forwards incomming packets to CLIENT_PORT after removing custom header
    xserver_handler_thread = threading.Thread(target=xserver_handler, args=(https_socket, ))
    xserver_handler_thread.start()



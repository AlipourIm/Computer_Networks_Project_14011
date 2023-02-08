# import requests
# import urllib3
# urllib3.disable_warnings()
# res = requests.get('https://localhost:443', verify='./certificate.pem')
# print(res)

import socket
import ssl

from PrettyLogger import logger_config
log = logger_config("webserver")

hostname = 'localhost'
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations("./keys/certificate.pem")

# Use two lines below instead of line above if you don't want to check self-signed certificate 
# context.verify_mode = ssl.CERT_NONE 
# context.check_hostname = False

with socket.create_connection((hostname, 443)) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        # print(ssock.version())
        ssock.sendall("GET / HTTP/1.1\r\nHost: localhost\r\n\r\n".encode("ASCII"))
        buffer = ssock.recv(1024)
        print(buffer.decode("UTF-8"))   
import socket
import ssl
from PrettyLogger import logger_config
import Constants
import threading
import time


log = logger_config("webserver")

xserver_socket: socket.socket
destination_lut = {}

def establish_HTTPS_connection() -> socket.socket:
    global xserver_socket
    sleep_time = 1
    while True:
        try:
            hostname = 'localhost'
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.load_verify_locations("./keys/certificate.pem")

            '''
            # Use two lines below instead of line above if you don't want to check self-signed certificate 
            context.verify_mode = ssl.CERT_NONE 
            context.check_hostname = False
            '''

            raw_sock = socket.create_connection((hostname, 443))
            https_socket = context.wrap_socket(raw_sock, server_hostname = Constants.X_SERVER_DOMAIN_NAME)
            xserver_socket = https_socket
        
            log.info("Conected to Xserver successfully.")
            return https_socket
        except ConnectionRefusedError:
            log.warning(f"Xserver is not responding... retrying in {sleep_time}")
            time.sleep(sleep_time)
            sleep_time *= 2

def client_handler():
    global xserver_socket, destination_lut
    UDP_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDP_server_socket.bind(("localhost", Constants.XCLIENT_UDP_PORT))
    
    
    while True:
        bytes_address_pair = UDP_server_socket.recvfrom(Constants.BUFFER_SIZE)
        message = bytes_address_pair[0].decode("ascii")

        if message[0:4] == "\0\0\0\0":
            _, server_address, server_port = message.split("\0\0\0\0", maxsplit=2)
            client_address, client_port = bytes_address_pair[1]
            destination_lut[client_port] = (server_address, server_port)
            https_message = f"GET / HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/zip\r\nContent-Length: {len(message)}\r\n\r\n{client_port}\r\n\r\n{destination_lut[client_port][0]}\r\n\r\n{destination_lut[client_port][1]}\r\n\r\n{message}"
            xserver_socket.sendall(https_message.encode("ascii"))
            log.info(f"client with {client_address}:{client_port} wants to connect to {server_address}:{server_port}.")
        else:
            client_port = bytes_address_pair[1][1]
            https_message = f"PUT / HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/zip\r\nContent-Length: {len(message)}\r\n\r\n{client_port}\r\n\r\n{destination_lut[client_port][0]}\r\n\r\n{destination_lut[client_port][1]}\r\n\r\n{message}"
            xserver_socket.sendall(https_message.encode("ascii"))


def xserver_handler():
    global xserver_socket
    try:
		# Create a UDP socket at server side, (ipv4, UDP)
        UDP_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        while True:
            buffer = xserver_socket.recv(Constants.BUFFER_SIZE).decode("ascii")
            log.info(f"message from xserver: {buffer.encode('ascii')}")

            arr = buffer.split("\r\n\r\n", maxsplit=2)
            https_header = arr[0]
            client_port = int(arr[1])
            UDP_message = arr[2]

			# Send to client using created UDP socket
            bytesToSend = str.encode(UDP_message)
            UDP_client_socket.sendto(bytesToSend, ("127.0.0.1", client_port))
			
    except KeyboardInterrupt:
        UDP_client_socket.close()
        log.info(f"XServer disconnected.")
    except IndexError:
        log.info(f"connection with server failed.")
        establish_HTTPS_connection()
        xserver_handler()   # Keep Xserver handler thread alive

if __name__ == "__main__":
    https_socket = establish_HTTPS_connection()

    # This thread listens on XCLIENT_UDP_PORT and forwards incomming packets to XSERVER after adding header
    client_handler_thread = threading.Thread(target=client_handler, args=())
    client_handler_thread.start()

    # This thread reads from HTTPS socket and forwards incomming packets to CLIENT_PORT after removing custom header
    xserver_handler_thread = threading.Thread(target=xserver_handler, args=())
    xserver_handler_thread.start()



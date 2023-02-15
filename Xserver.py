import socket
import ssl
import threading
from PrettyLogger import logger_config
import Constants
from email.utils import formatdate



log = logger_config("webserver")

xclient_socket: socket.socket
UDP_socket: socket.socket
destination_lut = {}
UDP_socket_lut = {}

def xclient_handler(client, address):
	log.info(f"Client with address {address} connected.")

	try:
		while True:
			buffer = client.recv(Constants.BUFFER_SIZE).decode("ascii")
			log.info(f"message from xclient: {buffer.encode('ascii')}")

			arr = buffer.split("\r\n\r\n", maxsplit=4)
			https_header = arr[0]
			client_port = int(arr[1])
			server_address = arr[2]
			server_port = int(arr[3])
			UDP_message = arr[4]

			if https_header[0:3] == "GET":
				UDP_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
				UDP_socket_lut[client_port] = UDP_server_socket
				destination_lut[client_port] = (server_address, server_port)

				# This thread listens on UDP_server_socket and forwards incomming packets to XCLIENT after adding header
				server_handler_thread = threading.Thread(target=server_handler, args=(UDP_server_socket, ))
				server_handler_thread.start()
			elif https_header[0:3] == "PUT":
				# Send to server using created UDP socket
				bytesToSend = str.encode(UDP_message)
				UDP_socket_lut[client_port].sendto(bytesToSend, (server_address, server_port))
				
	except KeyboardInterrupt or IndexError:
		client.close()
		log.info(f"Client with address {address} disconnected.")


def establish_https_connection() -> socket.socket:
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	server_socket = ssl.wrap_socket (server_socket,
	certfile='./keys/certificate.pem', keyfile="./keys/key.pem",
	server_side=True, ssl_version=ssl.PROTOCOL_TLS)

	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)	# This solves address aleady in use issue

	server_socket.bind(('localhost', 443))
	server_socket.listen(5)

	log.info("Server is listening on localhost:443")

	return server_socket

def https_client_handler(https_socket: socket.socket):
	global xclient_socket
	try:
		while True:
			client, address = https_socket.accept()
			xclient_socket = client
			handler_thread = threading.Thread(target=xclient_handler, args=(client, address))
			handler_thread.start()
	except KeyboardInterrupt:
		log.warning("terminating server")
		https_socket.close()

def server_handler(UDP_socket):
	global xclient_socket
	# UDP_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	# UDP_server_socket.bind(("localhost", xserver_UDP_port))
	# UDP_socket = UDP_server_socket
    
	while True:
		bytes_address_pair = UDP_socket.recvfrom(Constants.BUFFER_SIZE)
		message = bytes_address_pair[0].decode("ascii")
		https_message = f"HTTP/1.1 200 OK\r\nDate: {formatdate(timeval=None, localtime=False, usegmt=True)}\
		\r\nContent-Type: application/zip\r\nContent-Length: {len(message)}\r\n\r\n{message}"
		log.info(f"message to xclient: {https_message.encode('ascii')}")
		xclient_socket.sendall(https_message.encode("ascii"))

if __name__ == "__main__":
	https_socket = establish_https_connection()

	# This thread reads from HTTPS socket and forwards incomming packets to SERVER_PORT after removing custom header
	xclient_handler_thread = threading.Thread(target=https_client_handler, args=(https_socket, ))
	xclient_handler_thread.start()
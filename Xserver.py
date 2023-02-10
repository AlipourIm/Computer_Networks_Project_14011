import socket
import ssl
import threading
from PrettyLogger import logger_config
import Constants


log = logger_config("webserver")

def xclient_handler(client, address):
	log.info(f"Client with address {address} connected.")

	try:
		# Create a UDP socket at client side, (ipv4, UDP)
		UDP_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
		UDP_server_socket.bind(("127.0.0.1", Constants.XSERVER_UDP_PORT))

		while True:
			buffer = client.recv(Constants.BUFFER_SIZE).decode("ascii")
			log.info(f"message from xclient: {buffer.encode('ascii')}")
			client.send("HTTP/1.1 200 OK".encode("ascii"))

			arr = buffer.split("\r\n\r\n", maxsplit=1)
			https_header = arr[0]
			UDP_message = arr[1]

			# Send to server using created UDP socket
			bytesToSend = str.encode(UDP_message)
			UDP_server_socket.sendto(bytesToSend, ("127.0.0.1", Constants.SERVER_PORT))
			
	except KeyboardInterrupt:
		UDP_server_socket.close()
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
	try:
		while True:
			client, address = https_socket.accept()
			handler_thread = threading.Thread(target=xclient_handler, args=(client, address))
			handler_thread.start()
	except KeyboardInterrupt:
		log.warning("terminating server")
		https_socket.close()

if __name__ == "__main__":
	https_socket = establish_https_connection()

	# This thread reads from HTTPS socket and forwards incomming packets to SERVER_PORT after removing custom header
	xclient_handler_thread = threading.Thread(target=https_client_handler, args=(https_socket, ))
	xclient_handler_thread.start()
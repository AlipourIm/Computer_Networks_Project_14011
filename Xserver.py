import socket
import ssl
import threading

from PrettyLogger import logger_config
log = logger_config("webserver")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket = ssl.wrap_socket (server_socket,
certfile='./keys/certificate.pem', keyfile="./keys/key.pem",
server_side=True, ssl_version=ssl.PROTOCOL_TLS)

server_socket.bind(('127.0.0.1', 443))
server_socket.listen(5)

log.info("Server is listening on localhost:443")

def client_handler(client, address):
	log.info(f"Client with address {address} connected.")
	buffer = client.recv(1024).decode("ascii")
	print(buffer)
	client.send("HTTP/1.1 200 OK".encode("ascii"))

	client.close()
	log.info(f"Client with address {address} disconnected.")

try:
	while True:
		client, address = server_socket.accept()
		handler_thread = threading.Thread(target=client_handler, args=(client, address))
		handler_thread.start()
except KeyboardInterrupt:
	log.warning("saw keyboard interrupt")
	server_socket.close()
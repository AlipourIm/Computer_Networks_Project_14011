import socket
import ssl
import threading

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket = ssl.wrap_socket (server_socket,
certfile='./certificate.pem', keyfile="./key.pem",
server_side=True, ssl_version=ssl.PROTOCOL_TLS)

server_socket.bind(('127.0.0.1', 443))
server_socket.listen(5)

def client_handler(client, address):
	buffer = client.recv(1024)
	print(buffer)
	client.send("HTTP/1.1 200 OK".encode("ascii"))
	client.close()
	pass

while True:
	client, address = server_socket.accept()
	handler_thread = threading.Thread(target=client_handler, args=(client, address))
	handler_thread.start()
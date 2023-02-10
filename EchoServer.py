import socket
import Constants


localIP     = "127.0.0.1"

# Create a datagram socket: (ipv4, UDP)
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, Constants.SERVER_PORT))

print("UDP server up and listening")

# Listen for incoming datagrams
while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(Constants.BUFFER_SIZE)

    message = bytesAddressPair[0]

    address = bytesAddressPair[1]

    print(f"Message from Client: {message.decode('ascii')}")
    print(f"Client IP Address: {address}")

    # Sending a reply to client
    UDPServerSocket.sendto(message, address)
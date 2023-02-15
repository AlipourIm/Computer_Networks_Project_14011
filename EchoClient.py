import socket
import Constants


serverAddressPort = (Constants.SERVER_DOMAIN_NAME, Constants.SERVER_PORT)
xClientAddressPort = ("127.0.0.1", Constants.XCLIENT_UDP_PORT)
bufferSize = 1024

# Create a UDP socket at client side, (ipv4, UDP)
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# UDPClientSocket.bind(("127.0.0.1", Constants.CLIENT_PORT))

# Initial message
UDPClientSocket.sendto(f"\0\0\0\0{serverAddressPort[0]}\0\0\0\0{serverAddressPort[1]}".encode("ascii"), xClientAddressPort)

while True:
    # Send to server using created UDP socket
    bytesToSend = str.encode(input("Please write your message: "))
    UDPClientSocket.sendto(bytesToSend, xClientAddressPort)

    msgFromServer = UDPClientSocket.recvfrom(bufferSize)[0].decode("ascii")
    print(f"Message from Server: {msgFromServer}")

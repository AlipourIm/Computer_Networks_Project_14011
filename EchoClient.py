import socket
import Constants

bytesToSend = str.encode("Hello UDP Server")
serverAddressPort = (Constants.X_SERVER_DOMAIN_NAME, Constants.SERVER_PORT)
bufferSize = 1024

# Create a UDP socket at client side, (ipv4, UDP)
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.bind(("127.0.0.1", Constants.CLIENT_UDP_PORT))

while True:
    # Send to server using created UDP socket
    bytesToSend = str.encode(input("Please write your message: "))
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

    msgFromServer = UDPClientSocket.recvfrom(bufferSize)[0].decode("ascii")
    print(f"Message from Server: {msgFromServer}")

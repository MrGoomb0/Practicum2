import socket

# Kleine test script om shit naar server te sturen en testen dat die werkt
client = socket.create_connection(('localhost', 1025))
message = client.recv(1012)
print(message.decode())

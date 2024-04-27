import sys
import socket
import threading

# Run server on localhost
HOST_SERVER = 'localhost'


def main(port: int):
    addr = (HOST_SERVER, port)
    print(f'Starting SMTP server on port {port}')
    if socket.has_dualstack_ipv6():
        smtp_server = socket.create_server(
            addr, family=socket.AF_INET6, dualstack_ipv6=True)
    else:
        smtp_server = socket.create_server(addr)

    # Allow up to 5 connections in the queue
    smtp_server.listen(5)
    while True:
        (client_socket, client_address) = smtp_server.accept()
        print(f'Connection from {client_address}')
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()


def handle_client(client_socket: socket.socket, client_address: str):
    print(f'Handling connection from {client_address}')

    # 220 is the code for "Service ready" in SMTP also everything should end with \r\n
    client_socket.send(b'220 Welcome to the SMTP server!\r\n')
    return


def append(incoming_message: str, user: str):
    # Toevoegen format checking.
    fh = open(str(user) + "/my_mailbox.txt", 'a')
    fh.write(incoming_message + "\n")
    fh.close()


if __name__ == "__main__":
    if len(sys.argv) - 1 != 1:
        raise Exception(
            f"SMTP mail server expects 1 argument, {len(sys.argv) - 1} were given.")
    # Check toevoegen om te kijken of het argument een integer is.
    port = int(sys.argv[1])
    main(port)

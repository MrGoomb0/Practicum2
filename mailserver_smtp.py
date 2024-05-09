import sys
import socket
import threading
import json
import datetime

# Run server on localhost
HOST_SERVER = ''


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
        thread = threading.Thread(
            target=handle_client, args=(client_socket, client_address))
        thread.start()


def handle_client(client_socket: socket.socket, client_address: str):
    print(f'Handling connection from {client_address}')

    # 220 is the code for "Service ready" in SMTP also everything should end with \r\n
    client_socket.send('220 {} Service Ready\r\n'.format(
        HOST_SERVER).encode('utf-8'))

    # First message should be HELO, client must ensure its a valid domain
    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            break

        print(f'Received: {data}')
        # Normally we could just take the first 4 characters, but the assignment deviates from the specification so we cant do that
        command = data.strip().split(' ')[0]
        if command == 'HELO':
            client_socket.sendall(
                '250 OK Hello {} \r\n'.format(data[5:].strip()).encode('utf-8'))
        elif command == 'MAIL_FROM:':
            client_socket.sendall('250 {}\r\n'.format(
                data[11:].strip()).encode('utf-8'))
        elif command == 'RCPT_TO:':
            client_socket.sendall('250 Recipient OK\r\n'.encode('utf-8'))
        elif command == 'DATA':
            client_socket.sendall(
                '354 Enter mail, end with "." on a line by itself\r\n'.encode('utf-8'))
            incoming_message = []
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                incoming_message.append(data)
                if data == '.\r\n':
                    process_mail(incoming_message)
                    client_socket.sendall(
                        '250 OK Message accepted for delivery\r\n'.encode('utf-8'))
                    break
        elif command == 'QUIT':
            client_socket.sendall('221 {} closing connection\r\n'.format(
                HOST_SERVER).encode('utf-8'))
            client_socket.close()
            break
        else:
            client_socket.sendall('500 Command not recognized' + str(command) + '\r\n'.encode('utf-8'))


def process_mail(data: list[str]):
    sender = data[0].split(' ')[1].strip()
    receiver = data[1].split(' ')[1].strip()
    subject = data[2].split(' ')[1].strip()
    message = ''
    for i in range(3, len(data)):
        if data[i] == '.\r\n':
            break
        message += data[i].strip() + ' '
    user = receiver.split('@')[0]
    mail = {
        "From": sender,
        "To": receiver,
        "Subject": subject,
        "Received": datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        "Body": message
    }
    append(mail, user)


def append(incoming_message: str, user: str):
    file_path = f"{user}/my_mailbox.json"
    with open(file_path, "r") as file:
        data = json.load(file)
        data.append(incoming_message)

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    print(f"Appended to {file_path}")


if __name__ == "__main__":
    if len(sys.argv) - 1 != 1:
        raise Exception(
            f"SMTP mail server expects 1 argument, {len(sys.argv) - 1} were given.")
    port = int(sys.argv[1])
    main(port)

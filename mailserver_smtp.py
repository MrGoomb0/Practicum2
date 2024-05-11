import sys
import socket
import threading
import json
import datetime
import time
import filelock

# Run server on localhost
HOST_SERVER = ''


def main(port: int):
    addr = (HOST_SERVER, port)
    print(f'Starting SMTP server on port {port}')
    if socket.has_dualstack_ipv6():
        smtp_server = socket.create_server(addr, family=socket.AF_INET6, dualstack_ipv6=True)
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
    client_socket.send('220 {} Service Ready\r\n'.format(HOST_SERVER).encode('utf-8'))

    # First message should be HELO, client must ensure its a valid domain
    while True:
        commands = process_buffer(client_socket.recv(1024).decode('utf-8'))
        print(f'Received: {commands}')
        # Normally we could just take the first 4 characters, but the assignment deviates from the specification so we cant do that
        for command in commands:
            if command[:4] == 'HELO':
                client_socket.sendall('250 OK Hello {} \r\n'.format(command[5:].strip()).encode('utf-8'))
            elif command[:10] == 'MAIL_FROM:':
                client_socket.sendall('250 {}\r\n'.format(command[11:].strip()).encode('utf-8'))
            elif command[:8] == 'RCPT_TO:':
                client_socket.sendall('250 Recipient OK\r\n'.encode('utf-8'))
            elif command[:4] == 'DATA':
                client_socket.sendall('354 Enter mail, end with "." on a line by itself\r\n'.encode('utf-8'))
                incoming_message = []
                # Add the messages already taken from the buffer
                incoming_message += commands[1:]
                if '.' in incoming_message:
                    process_mail(incoming_message[:incoming_message.index('.')])
                    client_socket.sendall('250 OK Message accepted for delivery\r\n'.encode('utf-8'))
                    break
                while True:
                    data = process_buffer(client_socket.recv(1024).decode('utf-8'))
                    print(f'Received (inner loop): "{data}"')
                    incoming_message += data
                    if '.' in data:
                        process_mail(incoming_message[:incoming_message.index('.')])
                        client_socket.sendall('250 OK Message accepted for delivery\r\n'.encode('utf-8'))
                        break
            elif command == 'QUIT':
                client_socket.sendall('221 {} closing connection\r\n'.format(HOST_SERVER).encode('utf-8'))
                client_socket.close()
                return
            else:
                client_socket.sendall(('500 Command not recognized' + str(command) + '\r\n').encode('utf-8'))


def process_buffer(data: str):
    print(f'Processing buffer: "{data}"')
    commands = [command for command in data.split('\r\n') if command != '']
    print(commands)
    return commands


def process_mail(data: list[str]):
    print(f'Processing mail: {data}')
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
    lock = filelock.FileLock(f"{user}/my_mailbox.json.lock", timeout=1)
    try:
        lock.acquire(blocking=False)
        with open(file_path, "r") as file:
            data = json.load(file)
            data.append(incoming_message)
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
    finally:
        lock.release()
    print(f"Appended to {file_path}")


if __name__ == "__main__":
    if len(sys.argv) - 1 != 1:
        raise Exception(f"SMTP mail server expects 1 argument, {len(sys.argv) - 1} were given.")
    port = int(sys.argv[1])
    main(port)

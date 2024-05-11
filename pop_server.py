import sys
import socket
import threading
import json

HOST_SERVER = ''
user = ''


def main(port: int):
    addr = (HOST_SERVER, port)
    print(f'Starting POP server on port {port}')
    if socket.has_dualstack_ipv6():
        pop_server = socket.create_server(addr, family=socket.AF_INET6, dualstack_ipv6=True)
    else:
        pop_server = socket.create_server(addr)

    # Allow up to 5 connections in the queue
    pop_server.listen(5)
    while True:
        (client_socket, client_address) = pop_server.accept()
        print(f'Connection from {client_address}')
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()


def handle_client(client_socket, client_address):
    client_socket.sendall(b"+OK POP3 server ready\r\n")
    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            command = data.strip().upper()
            if command.startswith('USER'):
                if proccess_user_command(command):
                    client_socket.sendall(b"+OK User accepted\r\n")
                else:
                    client_socket.sendall(b"-ERR User not found\r\n")
            elif command.startswith('PASS'):
                if process_pass_command(command):
                    client_socket.sendall(b"+OK POP3 server is ready\r\n")
                else:
                    client_socket.sendall(b"-ERR Authentication failed\r\n")
            elif command.startswith('STAT'):
                client_socket.sendall(b"+OK 0 0\r\n")
            elif command.startswith('LIST'):
                client_socket.sendall(b"+OK 0 messages\r\n")
            elif command.startswith('RETR'):
                client_socket.sendall(b"-ERR No such message\r\n")
            elif command.startswith('DELE'):
                client_socket.sendall(b"-ERR No such message\r\n")
            elif command.startswith('RSET'):
                client_socket.sendall(b"+OK\r\n")
            elif command == 'QUIT':
                client_socket.sendall(b"+OK Goodbye\r\n")
                break
            else:
                client_socket.sendall(b"-ERR Command not recognized\r\n")
    except socket.error as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        client_socket.close()
        print(f"Closed connection from {client_address}")


def proccess_user_command(command: str):
    user = command.split(' ')[1]
    with open('userinfo.json', 'r') as file:
        data = json.load(file)
        for entry in data:
            if entry.split(' ')[0] == user:
                return True
    return False


def process_pass_command(command: str):
    password = command.split(' ')[1]
    with open('userinfo.json', 'r') as file:
        data = json.load(file)
        for entry in data:
            if entry.split(' ')[1] == password:
                return True
    return False


def process_stat_command(command: str):
    with open(f'{user}/my_mailbox.json', 'r') as file:
        data = json.load(file)
        total_bytes = sum(len(str(email).encode()) for email in data)
        return len(data), total_bytes


def process_list_command(command: str):
    # Check if there is a message number specified
    response = []
    if len(command.split(' ')) == 1:
        with open(f'{user}/my_mailbox.json', 'r') as file:
            data = json.load(file)
            total_bytes = 0
            for i, email in enumerate(data):
                byte_size = len(str(email).encode())
                total_bytes += byte_size
                print(f'{i + 1} {byte_size}')
                response.append(f'{i + 1} {byte_size}')
            response.insert(0, f'+OK {len(response)} messages ({total_bytes} octets)')
    else:
        message_number = int(command.split(' ')[1])
        with open(f'{user}/my_mailbox.json', 'r') as file:
            data = json.load(file)
            if message_number <= len(data):
                byte_size = len(str(data[message_number - 1]).encode())
                response.append(f'+OK {message_number} {byte_size}')
            else:
                response.append('-ERR No such message')
    return response


def process_retr_command(command: str):
    pass


def process_dele_command(command: str):
    pass


def process_rset_command(command: str):
    pass


if __name__ == "__main__":
    if len(sys.argv) - 1 != 1:
        raise Exception("POP server expects 1 argument, " + str(len(sys.argv - 1)) + " were given.")
    # Check toevoegen om te kijken of het argument een integer is.
    port = int(sys.argv[1])
    user = "Jakob"
    process_stat_command('test')
    main(port)

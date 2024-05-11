import sys
import socket
import threading
import json
import filelock

HOST_SERVER = ''  # Empty means all available interfaces


def main(port: int):
    """
    Starts the POP server on the specified port.

    Args:
    port (int): The port number on which the server will listen.
    """
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
    """
    Handles client requests and processes POP commands.

    Args:
    client_socket: The socket object for the client.
    client_address: The address of the client.
    """
    client_socket.sendall(b"+OK POP3 server ready\r\n")
    delete_index = set()
    user = ''
    try:
        while True:
            data = client_socket.recv(1024).decode()
            print(f"Received data: {data}")
            if not data:
                break
            command = data.strip()
            if command.startswith('USER'):
                if proccess_user_command(command):
                    user = command.split(' ')[1]
                    client_socket.sendall(b"+OK User accepted\r\n")
                else:
                    client_socket.sendall(b"-ERR User not found\r\n")
            elif command.startswith('PASS'):
                if process_pass_command(command):
                    client_socket.sendall(b"+OK POP3 server is ready\r\n")
                else:
                    client_socket.sendall(b"-ERR Authentication failed\r\n")
            elif command.startswith('STAT'):
                messages, total_bytes = process_stat_command(command, user)
                client_socket.sendall(f"+OK {messages} {total_bytes}\r\n".encode())
            elif command.startswith('LIST'):
                response = process_list_command(command, user)
                for line in response:
                    client_socket.sendall(f"{line}\r\n".encode())
            elif command.startswith('RETR'):
                email = process_retr_command(command, user)
                if email:
                    print(email)
                    client_socket.sendall(f"+OK {email}\r\n".encode())
                else:
                    client_socket.sendall(b"-ERR No such message\r\n")
            elif command.startswith('DELE'):
                email_index = int(command.split(' ')[1])
                delete_index.add(email_index)
                client_socket.sendall(b"+OK\r\n")
            elif command.startswith('RSET'):
                delete_index.clear()
                client_socket.sendall(b"+OK\r\n")
            elif command == 'QUIT':
                process_quit_command(delete_index, user)
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
    """
    Processes the USER command to verify user's existence.

    Args:
    command (str): The entire command received on the socket

    Returns:
    bool: True if user is found, False otherwise.
    """
    user = command.split(' ')[1]
    # Need to check lock so we dont read when another thread is writing
    acquire_lock('userinfo.json')
    with open('userinfo.json', 'r') as file:
        data = json.load(file)
        print(f'Trying to find "{user}" in {data}')
        for entry in data:
            if entry.split(' ')[0] == user:
                release_lock('userinfo.json')
                return True
    release_lock('userinfo.json')
    return False


def process_pass_command(command: str):
    """
    Processes the PASS command to verify user's password.

    Args:
    command (str): The entire command received on the socket

    Returns:
    bool: True if password is correct, False otherwise.
    """
    password = command.split(' ')[1]
    acquire_lock('userinfo.json')
    with open('userinfo.json', 'r') as file:
        data = json.load(file)
        for entry in data:
            if entry.split(' ')[1] == password:
                release_lock('userinfo.json')
                return True
    release_lock('userinfo.json')
    return False


def process_stat_command(command: str, user):
    """
    Processes the STAT command to get the number of messages and total bytes.

    Args:
    command (str): The entire command received on the socket
    user (str): The user that is logged in.

    Returns:
    tuple: A tuple containing the number of messages and the total bytes.
    """
    acquire_lock(f'{user}/my_mailbox.json')
    with open(f'{user}/my_mailbox.json', 'r') as file:
        data = json.load(file)
        total_bytes = sum(len(str(email).encode()) for email in data)
        release_lock(f'{user}/my_mailbox.json')
        return len(data), total_bytes


def process_list_command(command: str, user) -> list[str]:
    """
    Processes the LIST command to get the list of messages.

    Args:
    command (str): The entire command received on the socket
    user (str): The user that is logged in.

    Returns:
    list: A list of strings containing the response to the LIST command.
    """
    response = []
    acquire_lock(f'{user}/my_mailbox.json')
    if len(command.split(' ')) == 1:
        with open(f'{user}/my_mailbox.json', 'r') as file:
            data = json.load(file)
            total_bytes = 0
            for i, email in enumerate(data):
                byte_size = len(str(email).encode())
                total_bytes += byte_size
                print(f'{i} {byte_size}')
                response.append(f'{i} {byte_size}')
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
    response.append('.')
    release_lock(f'{user}/my_mailbox.json')
    return response


def process_retr_command(command: str, user):
    """
    Processes the RETR command to get the content of a message.

    Args:
    command (str): The entire command received on the socket
    user (str): The user that is logged in.

    Returns:
    str: The content of the message.
    """
    acquire_lock(f'{user}/my_mailbox.json')
    index = int(command.split(' ')[1])
    with open(f'{user}/my_mailbox.json', 'r') as file:
        data = json.load(file)
        if index <= len(data):
            release_lock(f'{user}/my_mailbox.json')
            return data[index - 1]
        else:
            release_lock(f'{user}/my_mailbox.json')
            return None


def process_quit_command(indices, user):
    """
    Processes the QUIT command to delete messages and save the mailbox.

    Args:
    indices (set): A set containing the indices of messages to delete.
    user (str): The user that is logged in.
    """
    acquire_lock(f'{user}/my_mailbox.json')
    with open(f'{user}/my_mailbox.json', 'r') as file:
        data = json.load(file)
        new_data = [email for i, email in enumerate(data) if i not in indices]
    with open(f'{user}/my_mailbox.json', 'w') as file:
        json.dump(new_data, file)
    release_lock(f'{user}/my_mailbox.json')


def acquire_lock(path):
    """
    Acquires a lock on a file.

    Args:
    path (str): The path to the file to lock.

    Returns:
    filelock.FileLock: The lock object.
    """
    lock = filelock.FileLock(f"{path}.lock", timeout=1)
    try:
        lock.acquire(blocking=False)
        return lock
    except filelock.Timeout:
        raise Exception("Could not acquire lock")


def release_lock(path):
    """
    Releases a lock on a file.

    Args:
    path (str): The path to the file to lock.
    """
    lock = filelock.FileLock(f"{path}.lock", timeout=1)
    lock.release()


if __name__ == "__main__":
    if len(sys.argv) - 1 != 1:
        raise Exception("POP server expects 1 argument, " + str(len(sys.argv - 1)) + " were given.")
    port = int(sys.argv[1])
    main(port)

import socket
import sys
import json
import random
import time
import filelock
import ast

USER_PATH = "userinfo.json"
SMTP_PORT = 1025
POP3_PORT = 2525

UNAVAILABLE_MESSAGE = "The server is not available right now, please try again later.\n"
ERROR_MESSAGE = "The server did not react as expected, please try again later."


def main(ip):
    """
    Starts a client who connects to servers on the given IP.

    Args:
    ip (str): The IP to connect with servers.
    """
    succesful = False
    while not succesful:
        succesful = registrationAndLogin()
    print("Please choose one of the following options.\n")
    while True:
        print("a) Mail Sending\nb) Mail Management\nc) Mail Searching\nd) Exit")
        action = input()
        if action.startswith("a)"):
            mailSending(ip)
        elif action.startswith("b)"):
            mailManagement(ip)
        elif action.startswith("c)"):
            mailSearching(ip)
        elif action.startswith("d)"):
            print("Exiting program.")
            exit()
        else:
            print("The requested action does not exist, please try again")


def registrationAndLogin():
    """
    Handles the local registration/ login of a new client.
    """
    print("Please choose one of the following options.\n")
    while True:
        print("a) Register\nb) Login")
        action = input()
        if action.startswith("a)"):
            username = input("Please enter username: ")
            if len(username.split(" ")) > 1:
                print("Username cannot contain spaces, please try again.")
                return False
            lock = filelock.FileLock(USER_PATH + ".lock", timeout=1)
            succesful = False
            while not succesful:
                try:
                    lock.acquire(blocking=False)
                    succesful = True
                except:
                    time.sleep(1.0)
            userlist = readFile(USER_PATH)
            for user in userlist:
                if username == user.split(" ")[0]:
                    print("Username already in use, please try again.")
                    lock.release()
                    return False
            password = input("Please enter password: ")

            if len(password.split(" ")) > 1:
                print("Password cannot contain spaces, please try again.")
                lock.release()
                return False
            else:
                userlist.append(username + " " + password)
                writeFile(USER_PATH, userlist)
                lock.release()
                print("Registration succesful!")
                return True

        if action.startswith("b)"):
            username = input("Please enter username: ")
            password = input("Please enter password: ")
            lock = filelock.FileLock(USER_PATH + ".lock", timeout=1)
            succesful = False
            while not succesful:
                try:
                    lock.acquire(blocking=False)
                    succesful = True
                except:
                    time.sleep(1.0)
            userlist = readFile(USER_PATH)
            for user in userlist:
                if username == user.split(" ")[0]:
                    if password == user.split(" ")[1]:
                        lock.release()
                        print("Login succesfull!")
                        return True
                    else:
                        lock.release()
                        print("Incorrect password, please try again.")
                        return False
            lock.release()
            print("Username not known, please try registring.")
            return False
        else:
            print("The requested action does not exist, please try again")


def createConnectionSMTP(ip):
    """
    Connects the client with the SMTP-server on the given IP.

    Args:
    ip: IP to connect with the server.
    """
    client = socket.create_connection((ip, SMTP_PORT))
    response = 0
    p = 1
    while True:
        server_message = client.recv(1024).decode("utf-8")
        if (
            response == 0
            and server_message.startswith("220")
            and server_message.endswith("Service Ready\r\n")
        ):
            hostname = server_message.split(" ")[1]
            if (hostname == ""):
                hostname = "localhost"
            client.sendall(("HELO " + str(hostname)).encode())
            response += 1
        elif response == 1 and server_message.startswith(
            "250 OK Hello " + str(hostname)
        ):
            return True, client
        else:
            client.close()
            awake = False
            while not awake:
                if random.uniform(0, 1) < p:
                    client = socket.create_connection((ip, SMTP_PORT))
                    awake = True
                else:
                    time.sleep(random.uniform(0, 1 / p))
                p = p / 2
            if p < 0.001:
                return False, None

def createConnectionPOP3(ip):
    """
    Connects the client with the POP3-server on the given IP.

    Args:
    ip: IP to connect with the server.
    """
    client = socket.create_connection((ip, POP3_PORT))
    p = 1
    while True:
        server_message = client.recv(1024).decode("utf-8")
        if (
            server_message.startswith("+OK")
            and server_message.endswith("POP3 server ready\r\n")
        ):
            return True, client
        else:
            client.close()
            awake = False
            while not awake:
                if random.uniform(0, 1) < p:
                    client = socket.create_connection((ip, POP3_PORT))
                    awake = True
                else:
                    time.sleep(random.uniform(0, 1 / p))
                p = p / 2
            if p < 0.001:
                return False, None


def sendMailToServer(
    client: socket, sender: str, receiver: str, subject: str, message: str
) -> bool:
    """
    Sends a mail through the SMTP-server to another client.
    
    Args:
    client: The socket object of the client.
    sender: The address of the sender.
    receiver: The address of the receiver.
    subject: The subject of the message.
    message: The message itself.
    """
    client.sendall(("MAIL_FROM: " + str(sender)).encode())
    response = 0
    while True:
        server_message = client.recv(1012).decode("utf-8")
        if response == 0 and server_message.startswith("250 " + str(sender)):
            response += 1
            client.sendall(("RCPT_TO: " + str(receiver)).encode())
        elif response == 1 and server_message.startswith("250 Recipient OK"):
            response += 1
            client.sendall(("DATA").encode())
        elif response == 2 and server_message.startswith(
            '354 Enter mail, end with "." on a line by itself'
        ):
            response += 1
            for line in range(0, len(message)):
                client.sendall((message[line] + "\r\n").encode())
        elif response == 3 and server_message.startswith(
            "250 OK Message accepted for delivery"
        ):
            client.sendall(("QUIT").encode())
            return True
        else:
            print(ERROR_MESSAGE)
            client.close()
            return False


def mailSending(ip) -> bool:
    """
    Handles the UI of the 'Mail Sending' action.

    Args:
    ip: IP to connect with the server.
    """
    succesfull, client = createConnectionSMTP(ip)
    if not succesfull:
        print(UNAVAILABLE_MESSAGE)
        return False

    print("Please enter the mail:")
    message = []
    line = input()
    message.append(line)
    while line != ".":
        line = input()
        message.append(line)

    (
        formatted_correctly,
        error_message,
        sender,
        receiver,
        subject,
    ) = messageFormatChecker(message)
    if not formatted_correctly:
        print("This is an incorrect format.")
        print(error_message)
        client.sendall(("QUIT").encode())
        return False
    else:
        succesfull = sendMailToServer(client, sender, receiver, subject, message)
        if succesfull:
            print("Mail sent succesfully.")
            return True
        else:
            return False


def serverAuthentication(client: socket, username: str, password: str):
    """
    Handles authentication of a user through the POP3 server.

    Args:
    client: The socket object for the client.
    username:  The username used for the authentication.
    password: The password used for the authentication.
    """
    client.send(("USER " + str(username)).encode())
    response = 0
    while True:
        incomming_data = client.recv(1012).decode()
        server_messages = [server_message for server_message in incomming_data.split('\r\n') if server_message != '']
        for server_message in server_messages:
            if response == 0 and server_message.startswith("+OK"):
                client.sendall(("PASS " + str(password)).encode())
                response += 1
            elif response == 1 and server_message.startswith("+OK POP3 server is ready"):
                print(server_message)
                return True
            else:
                print("Incorrect credentials, please try again.")
                username = input("Please insert username: ")
                password = input("Please insert password: ")
                client.sendall(("USER " + str(username)).encode())
                response = 0


def mailManagement(ip):
    """
    Handles the UI of the 'Mail Management' action.

    Args:
    ip: IP to connect with the server.
    """
    username = input("Please insert username: ")
    password = input("Please insert password: ")
    succesfull, client = createConnectionPOP3(ip)
    if not succesfull:
        print(UNAVAILABLE_MESSAGE)
        return
    # Tries to authenticate on the POP3 server
    succesfull = serverAuthentication(client, username, password)

    client.sendall("STAT".encode())
    received = False
    while not received:
        incomming_data = client.recv(1012).decode()
        server_messages = [server_message for server_message in incomming_data.split('\r\n') if server_message != '']
        for server_message in server_messages:
            if server_message.startswith("+OK") and server_message.split(" ")[1].isnumeric():
                message_count = int(server_message.split(" ")[1])
                received = True
        
    emails = []

    for i in range(0, message_count):
        client.sendall(("RETR " + str(i) + "\r\n").encode())
        server_message = client.recv(1012).decode('utf-8')
        if server_message.startswith("+OK"):
            emails.append(ast.literal_eval(server_message[4:]))

    # Shows the emails that are sent through by the POP3 server
    for n in range(0, len(emails)):
        print(
            str(n)
            + "-"
            + emails[n]["From"]
            + "-"
            + emails[n]["Received"]
            + "-"
            + emails[n]["Subject"]
            + "\n"
        )

    while True:
        command = input("/")
        if command.startswith("STAT"):
            client.sendall("STAT".encode())
            status = client.recv(1012).decode('utf-8')
            status = status.split(" ")
            count = status[1]
            size = status[2]
            print("Number of emails: " + count + "\n")
            print("Size of emails: " + size + " octets\n")
        elif command.startswith("LIST"):
            command = command.split(" ")
            if len(command) > 1:
                if not command[1].isnumeric():
                    print("Argument of 'LIST' should be 'None' or 'int'.")
                else:
                    client.sendall(("LIST " + command[1]).encode('utf-8'))
                    incomming_data = client.recv(1012).decode()
                    server_messages = [server_message for server_message in incomming_data.split('\r\n') if server_message != '']
                    for server_message in server_messages:
                        if server_message.startswith("+OK"):
                            server_message = server_message.split(" ")
                            print(
                                "Message: "
                                + server_message[1]
                                + " Size: "
                                + server_message[2]
                                + "\n"
                            )
                        elif server_messages.startswith("-ERR"):
                            print("Invalid message number.\n")
            else:
                client.sendall(("LIST").encode())
                server_message = client.recv(1012).decode()
                if server_message == ".\r\n":
                        print("No messages found.")
                else:
                        server_message = server_message.split(" ")
                        print(
                            "Message count: "
                            + server_message[1]
                            + " Size: "
                            + server_message[3][1:]
                            + " octets\n"
                        )
                        end = False
                        while not end:
                            incomming_data = client.recv(1012).decode()
                            server_messages = [server_message for server_message in incomming_data.split('\r\n') if server_message != '']    
                            for server_message in server_messages:
                                    if server_message == ".":
                                        end = True
                                    else:
                                        server_message = server_message.split(" ")
                                        print(
                                            "Message: "
                                            + server_message[0]
                                            + " Size: "
                                            + server_message[1]
                                            + " octets\n"
                                        )
        elif command.startswith("RETR"):
            command = command.split(" ")
            if len(command) < 2:
                print("'RETR' command should have an argument.")
            elif not command[1].isnumeric():
                print("Argument of 'RETR' should be integer")
            else:
                client.sendall(("RETR " + str(command[1])).encode())
                server_message = client.recv(1012).decode()
                if server_message.startswith("-ERR"):
                    print("Invalid message number.")
                else:
                    message = ast.literal_eval(server_message[4:])
                    print("From: " + message["From"])
                    print("To: " + message["To"])
                    print("Subject: " + message["Subject"])
                    print("Received: " + message["Received"])
                    print("Message: " + message["Body"])
        elif command.startswith("DELE"):
            if len(command) < 2:
                print("'DELE' command should have an argument.")
            elif not command.split(" ")[1].isnumeric():
                print("Argument of 'DELE' should be integer")
            else:
                client.sendall(("DELE " + str(command.split(" ")[1]) + "\r\n").encode())
                server_message = client.recv(1012).decode()
                if server_message.startswith("-ERR"):
                    print("Invalid message number.")
                else:
                    print("Message marked as 'deleted'.")
        elif command.startswith("RSET"):
            client.sendall(("RSET\r\n").encode())
        elif command.startswith("QUIT"):
            client.sendall(("QUIT").encode())
            return
        else:
            print("Invalid command, please try again.")


def mailSearching(ip):
    """
    Handles the UI of the 'Mail Searching' action.

    Args:
    ip: IP to connect with the server.
    """
    username = input("Please insert username: ")
    password = input("Please insert password: ")
    succesfull, client = createConnectionPOP3(ip)
    if not succesfull:
        print(UNAVAILABLE_MESSAGE)
        return
    # Tries to authenticate on the POP3 server
    succesfull = serverAuthentication(client, username, password)
    
    client.sendall("STAT".encode())
    received = False
    while not received:
        incomming_data = client.recv(1012).decode()
        server_messages = [server_message for server_message in incomming_data.split('\r\n') if server_message != '']
        for server_message in server_messages:
            if server_message.startswith("+OK") and server_message.split(" ")[1].isnumeric():
                message_count = int(server_message.split(" ")[1])
                received = True
        
    emails = []

    for i in range(0, message_count):
        client.sendall(("RETR " + str(i) + "\r\n").encode())
        server_message = client.recv(1012).decode('utf-8')
        if server_message.startswith("+OK"):
            emails.append(ast.literal_eval(server_message[4:]))

    print("Please choose one of the following options.")
    while True:
        print("a) Word/sentences\nb) Time\nc) Address")
        action = input()
        if action == "a)":
            target = input("Search term: ")
            for message in emails:
                if target in message["Body"] or target in message["Subject"]:
                    print(message + "\n")
            return
        elif action == "b)":
            target = input("Search term: ")
            if len(target.split("-")) != 3:
                print("Search criteria for time should be of the form 'yyyy-mm-dd'")
            elif len(target.split("-")[0]) != 4 or len(target.split("-")[1]) != 2 or len(target.split("-")[2]) != 2:
                print("Search criteria for time should be of the form 'yyyy-mm-dd'")
            else:
                for message in emails:
                    if target == message["Received"]:
                        print(message + "\n")
                return
        elif action == "c)":
            target = input("Search term: ")
            if len(target.split("@")) != 2:
                print("Search criteria for time should be of the form <username@domainname>")
            elif len(target.split("@")[1].split(".")) != 2:
                print("Search criteria for time should be of the form <username@domainname>")
            else:
                for message in emails:
                    if target == message["From"] or target == message["To"]:
                        print(message + "\n")
        else:
            print("The requested action does not exist, please try again")


def messageFormatChecker(message):
    """
    Checks if a given message is of the correct format.

    Args:
    message: The messages whose format is checked.
    """
    formatted_sender = None
    formatted_receiver = None
    formatted_subject = None
    format = message
    error_message = None
    # Check if the 4 items are included.
    if len(format) < 4:
        error_message = "One of the four manditory fields was not included."
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )

    # Check the format of the first line.
    sender = format[0].split(":")

    if len(sender) != 2:
        error_message = (
            "Expected 'From: <username>@<domain name>', but received '"
            + str(format[0])
            + "'."
        )
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )
    if sender[0] != "From":
        error_message = "Expected the first line to begin with 'From'."
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )
    if not sender[1].startswith(" "):
        error_message = "There should be a whitespace between 'From:' and '<username>@<domain name>'."
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )
    if len(sender[1].split("@")) != 2:
        error_message = "Expected that the sender exists out of two fields sperated by '@': '<username>' and '<domain name>'."
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )
    username, domain_name = sender[1].split("@")
    if len(username[1:].split(" ")) != 1:
        error_message = "Username should not include a whitespace."
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )
    if len(domain_name.split(".")) != 2:
        error_message = (
            "<domain name> should only have one appendix starting with '.' ."
        )
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )

    formatted_sender = sender[1][1:]

    # Check the format of the second line.
    receiver = format[1].split(":")
    if len(receiver) != 2:
        error_message = (
            "Expected 'To: <username>@<domain name>', but received '"
            + str(format[1])
            + "'."
        )
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )
    if receiver[0] != "To":
        error_message = "Expected the second line to begin with 'To'."
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )
    if not receiver[1].startswith(" "):
        error_message = (
            "There should be a whitespace between 'To:' and '<username>@<domain name>'."
        )
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )
    if len(receiver[1].split("@")) != 2:
        error_message = "Expected that the sender exists out of two fields sperated by '@': '<username>' and '<domain name>'."
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )
    username, domain_name = receiver[1].split("@")
    if len(username[1:].split(" ")) != 1:
        error_message = "Username should not include a whitespace."
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )
    if len(domain_name.split(".")) != 2:
        error_message = (
            "<domain name> should only have one appendix starting with '.' ."
        )
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )

    formatted_receiver = receiver[1][1:]

    # Check the third line.
    subject = format[2].split(":")
    if len(subject) != 2:
        error_message = (
            "Expected 'Subject: <subject string>', but received '"
            + str(format[2])
            + "'."
        )
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )
    if subject[0] != "Subject":
        error_message = "Expected thrid line to begin with 'Subject'."
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )
    if not subject[1].startswith(" "):
        error_message = (
            "There should be a whitespace between 'Subject:' and '<subject string>'."
        )
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )
    if len(subject[1][1:].split(" ")) != 1:
        error_message = "The '<subject string>' should not include a whitespace."
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )
    if len(subject[1]) > 50:
        error_message = "The '<subject string>' should be no longer than 50 characters."
        return (
            False,
            error_message,
            formatted_sender,
            formatted_receiver,
            formatted_subject,
        )

    formatted_subject = subject[1][1:]

    # Check if there is a full stop at the end, and if it is the only one.
    if format[-1] != ".":
        error_message = (
            "The message should end with a new line containing nothing but a full stop."
        )
        return False, error_message
    for i in range(0, len(format)):
        if format[i] == "." and i != len(format) - 1:
            error_message = (
                "There was an empty line containing nothing but a full stop at line "
                + str(i + 1)
                + ". Only the last line can be a full stop."
            )
            return (
                False,
                error_message,
                formatted_sender,
                formatted_receiver,
                formatted_subject,
            )

    return True, error_message, formatted_sender, formatted_receiver, formatted_subject


def readFile(path):
    """
    Function to open a JSON file.

    Args:
    path: Location of the JSON file.
    """
    fh = open(path, "r")
    return json.loads(fh.read())


def writeFile(path, data):
    """
    Function to wrtie to a JSON file.

    Args:
    path: Location of the JSON file.
    data: Data to write to the JSON file.
    """
    fh = open(path, "w")
    fh.write(json.dumps(data, indent=2))
    fh.close


if __name__ == "__main__":
    if len(sys.argv) - 1 != 1:
        raise Exception(
            "SMTP mail server expects 1 argument, "
            + str(len(sys.argv - 1))
            + " were given."
        )
    # Check toevoegen om te kijken of het argument een integer is.
    ip = sys.argv[1]
    main(ip)

import sys

def main(ip):
    succesful = False
    while not succesful:
        username = input("Please enter username: ")
        password = input("Please enter password: ")
        if (len(username.split(" ")) > 1) or (len(password.split(" ")) > 1):
            print("Username or password may not contain spaces, please try again.")
        else:
            fh = open('userinfo.txt', "a")
            fh.write(username + " " + password + "\n")
            print("Login succesful!")
            succesful = True
    print("Please choose one of the following options.\n")
    while True:
        print("a) Mail Sending\nb) Mail Management\nc) Mail Searching\nd) Exit")
        action = input()
        if action == 'Mail Sending':
            mailSending()
        elif action == 'Mail Management':
            mailManagement()
        elif action == 'Mail Searching':
            mailSearching()
        elif action == "Exit":
            print("Exiting program.")
            exit()
        else:
            print("The requested action does not exist, please try again")
    

def mailSending():
    print("please enter the mail:")
    message = input()
    formatted_correctly, error_message = messageFormatChecker(message)
    if not formatted_correctly:
        print("This is an incorrect format.\n")
        print(error_message)
        return False
    else:
        print("Mail sent succesfully.")
        return True
    
    

def mailManagement():
    return 0

def mailSearching():
    return 0

def messageFormatChecker(message) -> tuple[str, str|None]:
    format = message.split("\n")
    error_message = None
    #Check if the 4 items are included.
    if len(format) < 4:
        error_message = "One of the four manditory fields was not included."
        return False, error_message
    
    # Check the format of the first line.
    sender = format[0].split(":")
    if len(sender != 2):
        error_message = "Expected 'From: <username>@<domain name>', but received '" + str(format[0]) + "'." 
        return False, error_message
    if sender[0] != "From":
        error_message = "Expected the first line to begin with 'From'."
        return False, error_message
    if not sender[1].startswith(" "):
        error_message = "There should be a whitespace between 'From:' and '<username>@<domain name>'."
        return False, error_message
    if len(sender[1].split("@")) != 2: 
        error_message = "Expected that the sender exists out of two fields sperated by '@': '<username>' and '<domain name>'."
        return False, error_message
    username, domain_name = sender[1].split("@")
    if (len(username[1:].split(" ")) != 1): 
        error_message = "Username should not begin with a whitespace."
        return False, error_message
    if (len(domain_name.split(".")) != 2): 
        error_message = "<domain name> should only have one appendix starting with '.' ."
        return False, error_message

    # Check the format of the second line.
    receiver = format[1].plist(":")
    if len(receiver) != 2:
        error_message = "Expected 'To: <username>@<domain name>', but received '" + str(format[1]) + "'."
        return False, error_message
    if receiver[0] != "To":
        error_message = "Expected the second line to begin with 'To'."
        return False, error_message
    if not receiver[1].startswith(" "): 
        error_message = "There should be a whitespace between 'To:' and '<username>@<domain name>'."
        return False, error_message
    if len(receiver[1].split("@")) != 2:
        error_message = "Expected that the sender exists out of two fields sperated by '@': '<username>' and '<domain name>'."
        return False, error_message
    username, domain_name = receiver[1].split("@")
    if (len(username[1:].split(" ")) != 1):
        error_message = "Username should not begin with a whitespace."
        return False, error_message
    if (len(domain_name.split(".")) != 2): 
        error_message = "<domain name> should only have one appendix starting with '.' ."
        return False, error_message
    
    #Check the third line.
    subject = format[2].split(":")
    if len(subject) != 2:
        error_message = "Expected 'Subject: <subject string>', but received '" + str(format[2]) + "'."
        return False, error_message
    if subject[0] != "Subject":
        error_message = "Expected thrid line to begin with 'Subject'."
        return False, error_message
    if not subject[1].startswith(" "): 
        error_message = "There should be a whitespace between 'Subject:' and '<subject string>'."
        return False, error_message
    if len(subject[1][1:].split(" ")) != 1: 
        error_message = "The '<subject string>' should not begin with a whitespace."
        return False, error_message
    if len(subject[1] > 50):
        error_message = "The '<subject string>' should be no longer than 5° characters."
        return False, error_message
    
    #Check if there is a full stop at the end, and if it is the only one.
    if format[-1] != ".":
        error_message = "The message should end with a new line containing nothing but a full stop."
        return False, error_message
    for i in range(0,len(format)):
        if format(i) == "." and i != len(format) -1:
            error_message = "There was an empty line containing nothing but a full stop at line " + str(i) + ". Only the last line can be a full stop."
            return False, error_message
    
    return True, error_message

    

if __name__ == "__main__":
    if len(sys.argv) -1 != 1:
        raise Exception("SMTP mail server expects 1 argument, " + str(len(sys.argv-1)) + " were given.")
    # Check toevoegen om te kijken of het argument een integer is.
    ip = int(sys.argv[1])
    main(ip)


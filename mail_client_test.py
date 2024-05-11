import mail_client
import builtins


IP = 10
CORRECT_EMAIL = "From: eddy@gmail.com\nTo: eddy@gmail.com\nSubject: subject\n \n."


def test_registrationAndLogin_registration_correct(mocker):
    index = [-1]
    mockInputData = ["a)", "test", "Test123"]

    def mockInput(x="None"):
        index[0] = index[0] + 1
        return mockInputData[index[0]]

    mocker.patch("builtins.input", mockInput)
    mocker.patch("mail_client.writeFile", lambda x, y: None)
    SpyOnPrint = mocker.spy(builtins, "print")
    assert mail_client.registrationAndLogin() == True
    SpyOnPrint.assert_any_call("Registration succesful!")


def test_registrationAndLogin_registration_userAlreadyExists(mocker):
    index = [-1]
    mockInputData = ["a)", "Mataro", "Test123"]

    def mockInput(x="None"):
        index[0] = index[0] + 1
        return mockInputData[index[0]]

    mocker.patch("builtins.input", mockInput)
    mocker.patch("mail_client.writeFile", lambda x, y: None)
    SpyOnPrint = mocker.spy(builtins, "print")
    assert mail_client.registrationAndLogin() == False
    SpyOnPrint.assert_any_call("Username already in use, please try again.")


def test_registrationAndLogin_registration_userSpaces(mocker):
    index = [-1]
    mockInputData = ["a)", "te st", "Test123"]

    def mockInput(x="None"):
        index[0] = index[0] + 1
        return mockInputData[index[0]]

    mocker.patch("builtins.input", mockInput)
    mocker.patch("mail_client.writeFile", lambda x, y: None)
    SpyOnPrint = mocker.spy(builtins, "print")
    assert mail_client.registrationAndLogin() == False
    SpyOnPrint.assert_any_call("Username cannot contain spaces, please try again.")


def test_registrationAndLogin_registration_passwordSpaces(mocker):
    index = [-1]
    mockInputData = ["a)", "test", "Test 123"]

    def mockInput(x="None"):
        index[0] = index[0] + 1
        return mockInputData[index[0]]

    mocker.patch("builtins.input", mockInput)
    mocker.patch("mail_client.writeFile", lambda x, y: None)
    SpyOnPrint = mocker.spy(builtins, "print")
    assert mail_client.registrationAndLogin() == False
    SpyOnPrint.assert_any_call("Password cannot contain spaces, please try again.")


def test_registrationAndLogin_login_correct(mocker):
    index = [-1]
    mockInputData = ["b)", "Jakob", "NietTEST123!", "d)"]

    def mockInput(x="None"):
        index[0] = index[0] + 1
        return mockInputData[index[0]]

    mocker.patch("builtins.input", mockInput)
    mocker.patch("mail_client.writeFile", lambda x, y: None)
    SpyOnPrint = mocker.spy(builtins, "print")
    assert mail_client.registrationAndLogin() == True
    SpyOnPrint.assert_any_call("Login succesfull!")


def test_registrationAndLogin_login_userNotKnown(mocker):
    index = [-1]
    mockInputData = ["b)", "TEst", "NietTEST123!", "d)"]

    def mockInput(x="None"):
        index[0] = index[0] + 1
        return mockInputData[index[0]]

    mocker.patch("builtins.input", mockInput)
    mocker.patch("mail_client.writeFile", lambda x, y: None)
    SpyOnPrint = mocker.spy(builtins, "print")
    assert mail_client.registrationAndLogin() == False
    SpyOnPrint.assert_any_call("Username not known, please try registring.")


def test_registrationAndLogin_login_incorrectPassword(mocker):
    index = [-1]
    mockInputData = ["b)", "Jakob", "TEST123!", "d)"]

    def mockInput(x="None"):
        index[0] = index[0] + 1
        return mockInputData[index[0]]

    mocker.patch("builtins.input", mockInput)
    mocker.patch("mail_client.writeFile", lambda x, y: None)
    SpyOnPrint = mocker.spy(builtins, "print")
    assert mail_client.registrationAndLogin() == False
    SpyOnPrint.assert_any_call("Incorrect password, please try again.")


def test_mailSending_serverUnavailable(mocker):
    mocker.patch("mail_client.createConnection", lambda x, y: (False, None))
    SpyOnPrint = mocker.spy(builtins, "print")
    assert mail_client.mailSending("localhost") == False
    SpyOnPrint.assert_any_call(
        "The server is not available right now, please try again later.\n"
    )


def test_mailSending_incorrect(mocker):
    index = [-1]
    mockInputData = ["Wrong", "To: eddy@gmail.com", "Subject: test", "test", "."]

    def mockInput(x="None"):
        index[0] = index[0] + 1
        return mockInputData[index[0]]

    class trivial_socket:
        def sendall(x):
            return None

    mocker.patch("builtins.input", mockInput)
    mocker.patch("mail_client.createConnection", lambda x, y: (True, trivial_socket))
    mocker.patch("mail_client.sendMailToServer", lambda x, y, z, a, b: True)
    mocker.patch("socket.socket", trivial_socket)
    SpyOnPrint = mocker.spy(builtins, "print")
    assert mail_client.mailSending("localhost") == False
    SpyOnPrint.assert_any_call("This is an incorrect format.")


def test_mailSending_correct(mocker):
    index = [-1]
    mockInputData = [
        "From: eddy@gmail.com",
        "To: eddy@gmail.com",
        "Subject: test",
        "test",
        ".",
    ]

    def mockInput(x="None"):
        index[0] = index[0] + 1
        return mockInputData[index[0]]

    mocker.patch("builtins.input", mockInput)
    mocker.patch("mail_client.createConnection", lambda x, y: (True, None))
    mocker.patch("mail_client.sendMailToServer", lambda x, y, z, a, b: True)
    SpyOnPrint = mocker.spy(builtins, "print")
    assert mail_client.mailSending("localhost") == True
    SpyOnPrint.assert_any_call("Mail sent succesfully.")


def test_messageFormatChecker_missingField():
    assert (
        False,
        "One of the four manditory fields was not included.",
        None,
        None,
        None,
    ) == mail_client.messageFormatChecker([""])


def test_messageFormatChecker_errorLine1():
    message = "Wrong\n\n\n\n"
    message = message.split("\n")
    assert (
        False,
        "Expected 'From: <username>@<domain name>', but received 'Wrong'.",
        None,
        None,
        None,
    ) == mail_client.messageFormatChecker(message)
    message = "Wrong : test@gmail.com\n\n\n\n"
    message = message.split("\n")
    assert (
        False,
        "Expected the first line to begin with 'From'.",
        None,
        None,
        None,
    ) == mail_client.messageFormatChecker(message)
    message = "From:Wrong\n\n\n\n"
    message = message.split("\n")
    assert (
        False,
        "There should be a whitespace between 'From:' and '<username>@<domain name>'.",
        None,
        None,
        None,
    ) == mail_client.messageFormatChecker(message)
    message = "From: Wrong\n\n\n\n"
    message = message.split("\n")
    assert (
        False,
        "Expected that the sender exists out of two fields sperated by '@': '<username>' and '<domain name>'.",
        None,
        None,
        None,
    ) == mail_client.messageFormatChecker(message)
    message = "From:  Wrong@correct.be\n\n\n\n"
    message = message.split("\n")
    assert (
        False,
        "Username should not include a whitespace.",
        None,
        None,
        None,
    ) == mail_client.messageFormatChecker(message)
    message = "From: Correct@wrong.be.be\n\n\n\n"
    message = message.split("\n")
    assert (
        False,
        "<domain name> should only have one appendix starting with '.' .",
        None,
        None,
        None,
    ) == mail_client.messageFormatChecker(message)


def test_messageFormatChecker_errorLine2():
    message = "From: Correct@correct.be\nwrong\n\n\n"
    message = message.split("\n")
    assert (
        False,
        "Expected 'To: <username>@<domain name>', but received 'wrong'.",
        "Correct@correct.be",
        None,
        None,
    ) == mail_client.messageFormatChecker(message)
    message = "From: Correct@correct.be\nWrong: \n\n\n"
    message = message.split("\n")
    assert (
        False,
        "Expected the second line to begin with 'To'.",
        "Correct@correct.be",
        None,
        None,
    ) == mail_client.messageFormatChecker(message)
    message = "From: Correct@correct.be\nTo:Wrong\n\n\n"
    message = message.split("\n")
    assert (
        False,
        "There should be a whitespace between 'To:' and '<username>@<domain name>'.",
        "Correct@correct.be",
        None,
        None,
    ) == mail_client.messageFormatChecker(message)
    message = "From: Correct@correct.be\nTo: Wrong\n\n\n"
    message = message.split("\n")
    assert (
        False,
        "Expected that the sender exists out of two fields sperated by '@': '<username>' and '<domain name>'.",
        "Correct@correct.be",
        None,
        None,
    ) == mail_client.messageFormatChecker(message)
    message = "From: Correct@correct.be\nTo:  Wrong@wrong\n\n\n"
    message = message.split("\n")
    assert (
        False,
        "Username should not include a whitespace.",
        "Correct@correct.be",
        None,
        None,
    ) == mail_client.messageFormatChecker(message)
    message = "From: Correct@correct.be\nTo: Correct@wrong.be.be\n\n\n"
    message = message.split("\n")
    assert (
        False,
        "<domain name> should only have one appendix starting with '.' .",
        "Correct@correct.be",
        None,
        None,
    ) == mail_client.messageFormatChecker(message)


def test_messageFormatChecker_errorLine3():
    message = "From: Correct@correct.be\nTo: Correct@correct.be\nWrong\n"
    message = message.split("\n")
    assert (
        False,
        "Expected 'Subject: <subject string>', but received 'Wrong'.",
        "Correct@correct.be",
        "Correct@correct.be",
        None,
    ) == mail_client.messageFormatChecker(message)
    message = "From: Correct@correct.be\nTo: Correct@correct.be\nWrong: correct\n"
    message = message.split("\n")
    assert (
        False,
        "Expected thrid line to begin with 'Subject'.",
        "Correct@correct.be",
        "Correct@correct.be",
        None,
    ) == mail_client.messageFormatChecker(message)
    message = "From: Correct@correct.be\nTo: Correct@correct.be\nSubject:Wrong\n"
    message = message.split("\n")
    assert (
        False,
        "There should be a whitespace between 'Subject:' and '<subject string>'.",
        "Correct@correct.be",
        "Correct@correct.be",
        None,
    ) == mail_client.messageFormatChecker(message)
    message = "From: Correct@correct.be\nTo: Correct@correct.be\nSubject:  Wrong\n"
    message = message.split("\n")
    assert (
        False,
        "The '<subject string>' should not include a whitespace.",
        "Correct@correct.be",
        "Correct@correct.be",
        None,
    ) == mail_client.messageFormatChecker(message)
    message = "From: Correct@correct.be\nTo: Correct@correct.be\nSubject: WWWWWWWWWWWWWWWWWWWWWWWWRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRROOOOOOOOOOOOONNNNNNNNNNNNNNNNNNNNNNNNNNNGGGGGGGGGGGGGGGGGGGGGGGGGGg\n"
    message = message.split("\n")
    assert (
        False,
        "The '<subject string>' should be no longer than 50 characters.",
        "Correct@correct.be",
        "Correct@correct.be",
        None,
    ) == mail_client.messageFormatChecker(message)


def test_messageFormatChecker_errorLine4():
    message = "From: Correct@correct.be\nTo: Correct@correct.be\nSubject: Correct\n"
    message = message.split("\n")
    assert (
        False,
        "The message should end with a new line containing nothing but a full stop.",
    ) == mail_client.messageFormatChecker(message)
    message = "From: Correct@correct.be\nTo: Correct@correct.be\nSubject: Correct\n.\n."
    message = message.split("\n")
    assert (
        False,
        "There was an empty line containing nothing but a full stop at line 4. Only the last line can be a full stop.",
        "Correct@correct.be",
        "Correct@correct.be",
        "Correct",
    ) == mail_client.messageFormatChecker(message)

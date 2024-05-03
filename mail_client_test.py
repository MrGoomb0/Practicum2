from mail_client import *
import builtins


IP = 10
CORRECT_EMAIL = "From: eddy@gmail.com\nTo: eddy@gmail.com\nSubject: subject\n \n."

def test_registration_correct(mocker):
    mocker.patch('builtins.input', lambda _: "Test")
    mocker.patch('mail_client.writeFile', lambda x, y: None)
    SpyOnPrint = mocker.spy(builtins, 'print')
    assert(registration() == True)
    SpyOnPrint.assert_called_once_with("Login succesful!")

def test_registration_incorrect(mocker):
    mocker.patch('builtins.input', lambda _: "Test 1234")
    SpyOnPrint = mocker.spy(builtins, 'print')
    assert(registration() == False)
    SpyOnPrint.assert_called_once_with("Username or password cannot contain spaces, please try again.")

def test_mailSending_corregitct(mocker):
    mocker.patch('builtins.input', lambda :"Wrong!")
    SpyOnPrint = mocker.spy(builtins, 'print')
    assert(mailSending() == False)
    SpyOnPrint.assert_any_call("please enter the mail:")
    SpyOnPrint.assert_any_call("This is an incorrect format.\n")
    SpyOnPrint.assert_any_call("One of the four manditory fields was not included.")

def test_mailSending_incorrect(mocker):
    mocker.patch('builtins.input', lambda :CORRECT_EMAIL)
    SpyOnPrint = mocker.spy(builtins, 'print')
    assert(mailSending() == True)
    SpyOnPrint.assert_any_call("please enter the mail:")
    SpyOnPrint.assert_any_call("Mail sent succesfully.")

def test_messageFormatChecker_missingField():
    assert((False, "One of the four manditory fields was not included.") == messageFormatChecker(""))

def test_messageFormatChecker_errorLine1():
    message = "Wrong\n\n\n\n"
    assert((False, "Expected 'From: <username>@<domain name>', but received 'Wrong'.") == messageFormatChecker(message))
    message = "Wrong : test@gmail.com\n\n\n\n"
    assert((False, "Expected the first line to begin with 'From'.") == messageFormatChecker(message))
    message = "From:Wrong\n\n\n\n"
    assert((False, "There should be a whitespace between 'From:' and '<username>@<domain name>'.") == messageFormatChecker(message))
    message = "From: Wrong\n\n\n\n"
    assert((False, "Expected that the sender exists out of two fields sperated by '@': '<username>' and '<domain name>'.") == messageFormatChecker(message))
    message = "From:  Wrong@correct.be\n\n\n\n"
    assert((False, "Username should not include a whitespace.") == messageFormatChecker(message))
    message = "From: Correct@wrong.be.be\n\n\n\n"
    assert((False, "<domain name> should only have one appendix starting with '.' .") == messageFormatChecker(message))

def test_messageFormatChecker_errorLine2():
    message = "From: Correct@correct.be\nwrong\n\n\n"
    assert((False, "Expected 'To: <username>@<domain name>', but received 'wrong'.") == messageFormatChecker(message))
    message = "From: Correct@correct.be\nWrong: \n\n\n"
    assert((False, "Expected the second line to begin with 'To'.") == messageFormatChecker(message))
    message = "From: Correct@correct.be\nTo:Wrong\n\n\n"
    assert((False, "There should be a whitespace between 'To:' and '<username>@<domain name>'.") == messageFormatChecker(message))
    message = "From: Correct@correct.be\nTo: Wrong\n\n\n"
    assert((False,  "Expected that the sender exists out of two fields sperated by '@': '<username>' and '<domain name>'.") == messageFormatChecker(message))
    message = "From: Correct@correct.be\nTo:  Wrong@wrong\n\n\n"
    assert((False,  "Username should not include a whitespace.") == messageFormatChecker(message))
    message = "From: Correct@correct.be\nTo: Correct@wrong.be.be\n\n\n"
    assert((False, "<domain name> should only have one appendix starting with '.' .") == messageFormatChecker(message))

def test_messageFormatChecker_errorLine3():
    message = "From: Correct@correct.be\nTo: Correct@correct.be\nWrong\n"
    assert((False, "Expected 'Subject: <subject string>', but received 'Wrong'.") == messageFormatChecker(message))
    message = "From: Correct@correct.be\nTo: Correct@correct.be\nWrong: correct\n"
    assert((False, "Expected thrid line to begin with 'Subject'.") == messageFormatChecker(message))
    message = "From: Correct@correct.be\nTo: Correct@correct.be\nSubject:Wrong\n"
    assert((False,  "There should be a whitespace between 'Subject:' and '<subject string>'.") == messageFormatChecker(message))
    message = "From: Correct@correct.be\nTo: Correct@correct.be\nSubject:  Wrong\n"
    assert((False, "The '<subject string>' should not include a whitespace.") == messageFormatChecker(message))
    message = "From: Correct@correct.be\nTo: Correct@correct.be\nSubject: WWWWWWWWWWWWWWWWWWWWWWWWRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRROOOOOOOOOOOOONNNNNNNNNNNNNNNNNNNNNNNNNNNGGGGGGGGGGGGGGGGGGGGGGGGGGg\n"
    assert((False, "The '<subject string>' should be no longer than 50 characters.") == messageFormatChecker(message))

def test_messageFormatChecker_errorLine4():
    message = "From: Correct@correct.be\nTo: Correct@correct.ne\nSubject: Correct\n"
    assert((False, "The message should end with a new line containing nothing but a full stop.") == messageFormatChecker(message))
    message = "From: Correct@correct.be\nTo: Correct@correct.ne\nSubject: Correct\n.\n."
    assert((False, "There was an empty line containing nothing but a full stop at line 4. Only the last line can be a full stop.") == messageFormatChecker(message))
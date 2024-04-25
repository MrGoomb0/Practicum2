import sys 

def main():
    return 0

if __name__ == "__main__":
    if len(sys.argv)-1 != 1:
        raise Exception("SMTP mail server expects 1 argument, " + str(len(sys.argv-1)) + " were given.")
    # Check toevoegen om te kijken of het argument een integer is.
    port = int(sys.argv[1])
    main(port)
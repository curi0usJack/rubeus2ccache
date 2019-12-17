class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class msg:
    def ok(self, message):
        print(bcolors.OKBLUE + "[*] {}".format(message) + bcolors.ENDC)

    def warn(self, message):
        print(bcolors.WARNING + "[!] {}".format(message) + bcolors.ENDC)

    def error(self, message):
        print(bcolors.FAIL + "[!] {}".format(message) + bcolors.ENDC)

    def success(self, message):
        print(bcolors.OKGREEN + "[+] {}".format(message) + bcolors.ENDC)

    def debug(self, message):
        if (args.debug):
            print(bcolors.WARNING + "[-] DEBUG: {}".format(message) + bcolors.ENDC)
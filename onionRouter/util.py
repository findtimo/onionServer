class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Util:
    def print_green(self,message):
        print('\033[92m' + str(message) + '\033[0m')

    def print_red(self,message):
        print('\033[1m\033[91m' + str(message) + '\033[0m')

    def print_yellow(self,message):
        print('\033[1m\033[93m' + str(message) + '\033[0m')

    def print_blue(self, message):
        print('\033[1m\033[94m' + str(message) + '\033[0m')

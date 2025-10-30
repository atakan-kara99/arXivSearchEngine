import cowsay
import unicodedata
from se.main import SearchEngine

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

if __name__ == '__main__':
    cowsay.tux('Please be patient! This could take a while..     Go get a coffee or brainstorm while shitting')

    se = SearchEngine()
    se.create_index('authors')
    print(f"Building index for authors ... {bcolors.OKGREEN} [\u2713] SUCCESSFUL!{bcolors.ENDC}")
    # se.create_index('title')
    print(f"Building index for titles ... {bcolors.OKGREEN} [\u2713] SUCCESSFUL!{bcolors.ENDC}")
    # se.create_index('abstract')
    print(f"Building index for abstracts ... {bcolors.OKGREEN} [\u2713] SUCCESSFUL!{bcolors.ENDC}")
    cowsay.cow("That was a loooong time! Sorry for that!")


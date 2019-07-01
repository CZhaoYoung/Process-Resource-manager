
from shell import Shell
import sys

if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)

    if argc == 1:
        Shell()
    elif argc == 2:
        Shell(argv[1])
    elif argc == 3:
        Shell(argv[1], argv[2])
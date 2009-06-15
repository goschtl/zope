# import

from van.reposync import main

def runit(string):
    "Test run a command"
    exitcode = main(string.split())
    if exitcode != 0:
        return exitcode

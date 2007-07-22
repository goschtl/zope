#!bin/env python

import os
import cStringIO
import sys

usage =  """
Usage: tools.py [action] [option]

Actions
-------

--dist will create and upload eggs
--test will cd into each folder and run bin/test
--help will show this message

Options
-------

--all will run action on all directories

Default action is --tests
Default option is --all

"""

action = '--test'
option = '--all'

actions = ['--dist', '--test', '--help']
options = ['--all']

args = sys.argv
for arg in sys.argv:
    if arg in actions:
        action = arg
    if arg in options:
        option = arg

if action == '--help':
    print usage
    sys.exit()

def main(action, option):
    dirs = [d for d in os.listdir('.') if os.path.isdir(d)]
    packages = []
    for package in dirs:
        path = os.path.join(os.getcwd(), package)
        if not path.endswith('.svn') and not path.endswith('.'):
            packages.append(path)
    for package in packages:
        os.chdir(package)
        if action == '--test':
            print "Running tests in directory %s" % package
            os.system('./bin/test -vv')


main(action, option)


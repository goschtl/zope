##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import pdb
import sys
import zc.monitor

class FakeStdout(object):
    def __init__(self, connection):
        self.connection = connection

    def write(self, *args):
        return self.connection.write(*args)


debugger = fakeout = None

def reset(connection):
    global debugger
    global fakeout

    fakeout = FakeStdout(connection.connection)
    debugger = pdb.Pdb(stdin=None, stdout=fakeout)
    debugger.reset()
    debugger.setup(sys._getframe(), None)


def command(connection, *args):
    global debugger
    global fakeout

    # if we haven't set up a debugger yet, do so
    if debugger is None:
        reset(connection)

    # if the user wants us to rebuild the debugger, do it
    if args and args[0] == 'reset':
        reset(connection)
    elif args and args[0] == 'debug':
        connection.write('the "debug" command is not supported\n')
    elif args and args[0] == 'quit':
        debugger = fakeout = None
        return zc.monitor.QUIT_MARKER
    else:
        debugger.onecmd(' '.join(args))

    connection.write(debugger.prompt)
    return zc.monitor.MORE_MARKER

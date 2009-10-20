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

class FakeStdout(object):
    def __init__(self, connection):
        self.connection = connection

    def flush(self):
        pass

    def write(self, *args):
        return self.connection.write(*args)


debugger = fakeout = None


def command(lines, *args):
    global debugger
    global fakeout
    if debugger is None:
        fakeout = FakeStdout(lines.connection)
        debugger = pdb.Pdb(stdin=None, stdout=fakeout)
        debugger.reset()
        debugger.setup(sys._getframe().f_back, None)

    debugger.onecmd(' '.join(args))

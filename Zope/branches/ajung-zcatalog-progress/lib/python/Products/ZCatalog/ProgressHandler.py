##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""
$Id: ZCatalog.py 25050 2004-05-27 15:06:40Z chrisw $
"""

import time, sys
from zLOG import LOG, INFO

from Interface import Interface

class IProgressHandler(Interface):
    """ A handler to log progress informations for long running 
        operations.
    """

    def init(ident, max):
        """ Called at the start of the long running process.

            'ident' -- a string identifying the operation
            'max' -- maximum number of objects to be processed (int)
        """ 

    def finish():
        """ Called up termination """

    def report(current, *args, **kw):
        """ Called for every iteration.

            'current' -- an integer representing the number of objects 
                         processed so far.
        """

    def output(text):
        """ Log 'text' to some output channel """        


class StdoutHandler:
    """ A simple progress handler """

    __implements__ = IProgressHandler

    def __init__(self, steps=100):
        self._steps = steps

    def init(self, ident, max):
        self._ident = ident
        self._max = max
        self._start = time.time()
        self.fp = sys.stdout
        self.output('Process started (%d objects to go)' % self._max)

    def finish(self):
        self.output('Process terminated. Duration: %0.2f seconds' % \
                    (time.time() -self._start))

    def report(self, current, *args, **kw):
        if current % self._steps == 0: 
            self.output('%d/%d (%.2f%%)' % (current, self._max, (100.0 * current / self._max)))

    def output(self, text):
        print >>self.fp, '%s: %s' % (self._ident, text)


class ZLogHandler(StdoutHandler):
    """ Use zLOG """

    __implements__ = IProgressHandler

    def output(self, text):
        LOG(self._ident, INFO, text)


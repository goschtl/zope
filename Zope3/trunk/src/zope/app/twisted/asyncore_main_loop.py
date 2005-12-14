##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Run the asyncore main loop

This module provides a function that tries to run the asyncore main loop.

If the asyncore socket map is empty when the function is called, then the
function exits immediately:

    >>> run(None)

If the loop dies due to an exception, then a panic is logged anf the failure
handler passed is called:

    >>> def failed():
    ...     print "FAILED!"

    >>> import asyncore
    >>> class BadDispatcher(asyncore.dispatcher):
    ...     _fileno = 42
    ...     def readable(self):
    ...         raise SystemError("I am evil")

    >>> import zope.testing.loggingsupport
    >>> handler = zope.testing.loggingsupport.InstalledHandler('ZEO.twisted')

    >>> BadDispatcher().add_channel()

    >>> run(failed)
    FAILED!

    >>> print handler
    ZEO.twisted CRITICAL
      The asyncore main loop died unexpectedly!

    >>> print handler.records[0].exc_info[1]
    I am evil

$Id$
"""

import logging
import sys
import threading

import ThreadedAsync
logger = logging.getLogger('ZEO.twisted')

def run(onerror):
    try:
        ThreadedAsync.loop()
    except:
        exc_info = sys.exc_info()
        logger.critical("The asyncore main loop died unexpectedly!",
                        exc_info = exc_info,
                        )
        onerror()
    
def run_in_thread(reactor):
    thread = threading.Thread(
        target=run,
        args=(reactor, ),
        )
    thread.setDaemon(True)
    thread.start()

        

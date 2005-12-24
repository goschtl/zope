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

If the handler passed is invalid, another panic will be logged:

    >>> run(None)

    >>> print handler
    ZEO.twisted CRITICAL
      The asyncore main loop died unexpectedly!
    ZEO.twisted CRITICAL
      The asyncore main loop died unexpectedly!
    ZEO.twisted CRITICAL
      Couldn't call error handler when asyncore main loop died unexpectedly!

    >>> print handler.records[-1].exc_info[1]
    'NoneType' object is not callable
   

$Id$
"""

import logging
import sys

# We're using thread, rather than threading because there seem to be
# some end-of-process cleanup problems with the threading module that
# cause weird unhelpful messages to get written to standard error
# intermittently when Python is exiting.  We'll leave the old threading
# code around in case it's helpful later.

## import threading 
import thread

import ThreadedAsync
logger = logging.getLogger('ZEO.twisted')

def run(onerror):
    try:
        ThreadedAsync.loop()
    except:
        exc_info = sys.exc_info()
        try:
            logger.critical("The asyncore main loop died unexpectedly!",
                            exc_info = exc_info,
                            )
            try:
                onerror()
            except:
                exc_info = sys.exc_info()
                logger.critical("Couldn't call error handler"
                                " when asyncore main loop died unexpectedly!",
                                exc_info = exc_info,
                                )
        except:
            # Yeah, this is a bare except, but there are reasonable
            # tests for the stuff inside and we need this to prevent spurious
            # errors on shutdown. :(
            pass
    
def run_in_thread(reactor):
# see note above
##     thread = threading.Thread(
##         target=run,
##         args=(reactor, ),
##         )
##     thread.setDaemon(True)
##     thread.start()
    thread.start_new_thread(run, (reactor, ))

        

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
"""zope.thread

Implements thread global variables.
"""

import threading
from zope.interface import moduleProvides, implements
from zope.thread.interfaces import IZopeThreadAPI
from zope.thread.interfaces import IInteractionThreadGlobal, ISiteThreadGlobal

__metaclass__ = type

moduleProvides(IZopeThreadAPI)


def thread_globals(thread=None):
    """See IZopeThreadAPI."""
    if thread is None:
        thread = threading.currentThread()
    if not hasattr(thread, '__zope3_thread_globals__'):
        thread.__zope3_thread_globals__ = ThreadGlobals()
    return thread.__zope3_thread_globals__


class ThreadGlobals:
    implements(IInteractionThreadGlobal, ISiteThreadGlobal)

    interaction = None
    site = None


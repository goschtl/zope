##############################################################################
#
# Copyright (c) 2005-2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""A ZODB storage that allows tracing the calls going to the real storage.

"""
__docformat__ = "reStructuredText"

from zope.interface import Interface
from zope.interface import Attribute
from zope.interface import implements

    #A subclass must define the following methods:
    #load()
    #store()
    #close()
    #cleanup()
    #lastSerial()
    #lastTransaction()
    #
    #It must override these hooks:
    #_begin()
    #_vote()
    #_abort()
    #_finish()
    #_clear_temp()
    #
    #If it stores multiple revisions, it should implement
    #loadSerial()
    #loadBefore()
    #iterator()
    #
    #If the subclass wants to implement undo, it should implement the
    #multiple revision methods and:
    #undo()
    #undoInfo()
    #undoLog()
    #
    #If the subclass wants to implement versions, it must implement:
    #abortVersion()
    #commitVersion()
    #modifiedInVersion()
    #versionEmpty()
    #versions()

class ITracingStorageEvent(Interface):
    """base IF for events
    all derived events will have the name
    ITracingStorageEvent_<method name>"""
    args = Attribute("Arguments")
    kw = Attribute("Keyword Arguments")
    result = Attribute("Base storage call result")

class ITracingStorageEvent_load(ITracingStorageEvent):
    pass

class ITracingStorageEvent_store(ITracingStorageEvent):
    pass

class ITracingStorageEvent_close(ITracingStorageEvent):
    pass

class ITracingStorageEvent_cleanup(ITracingStorageEvent):
    pass

class ITracingStorageEvent_lastSerial(ITracingStorageEvent):
    pass

class ITracingStorageEvent_lastTransaction(ITracingStorageEvent):
    pass

class TracingStorageEvent(object):
    """base class for events
    all derived events will have the name
    TracingStorageEvent_<method name>"""
    
    implements(ITracingStorageEvent)
    
    def __init__(self, result_=None, *args, **kw):
        self.args = args
        self.kw = kw
        self.result = result_

class TracingStorageEvent_load(TracingStorageEvent):
    implements(ITracingStorageEvent_load)

class TracingStorageEvent_store(TracingStorageEvent):
    implements(ITracingStorageEvent_store)

class TracingStorageEvent_close(TracingStorageEvent):
    implements(ITracingStorageEvent_close)

class TracingStorageEvent_cleanup(TracingStorageEvent):
    implements(ITracingStorageEvent_cleanup)

class TracingStorageEvent_lastSerial(TracingStorageEvent):
    implements(ITracingStorageEvent_lastSerial)

class TracingStorageEvent_lastTransaction(TracingStorageEvent):
    implements(ITracingStorageEvent_lastTransaction)

EVENTMAP = {
    'load': TracingStorageEvent_load,
    'store': TracingStorageEvent_store,
    'close': TracingStorageEvent_close,
    'cleanup': TracingStorageEvent_cleanup,
    'lastSerial': TracingStorageEvent_lastSerial,
    'lastTransaction': TracingStorageEvent_lastTransaction
}
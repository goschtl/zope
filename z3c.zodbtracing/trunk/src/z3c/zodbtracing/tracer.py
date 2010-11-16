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

import os
import time
import pprint
import traceback
import threading
import cStringIO

class baseStatCollector(object):
    """base class for collecting info
    subclass and override"""
    def initCalled(self):
        pass
    
    def methodCalled(self, methodName, result_, *args, **kw):
        pass

class textStatCollector(baseStatCollector):
    """WARNING!!!
    this class will dump a HUGE amount of data to the text file,
    so be careful!!!
    By default it dumps also a stack traceback too!
    """
    
    fhnd = None # will be closed when the object gets destroyed
    counter = 0 # might be useful to set breakpoints
    printTB = True # dump traceback?
    txtFileName = None
    
    def __init__(self, txtFileName):
        self.txtFileName = txtFileName
        
        #create+truncate the file
        open(txtFileName, 'wb').close()
        
        #seems that methods can be called from multiple threads
        #that breaks havoc with file write buffering
        l = threading.Lock()
        self._lock_acquire = l.acquire
        self._lock_release = l.release
    
    def _printTB(self):
        if self.printTB:
            self.fhnd.write("Traceback:\n")
            traceback.print_stack(file=self.fhnd)
    
    def _print(self, header, value):
        self.fhnd.write("%s\n" % header)
        tmp = cStringIO.StringIO()
        pprint.pprint(value, tmp)
        if tmp.tell()>512:
            tmp.seek(0)
            self.fhnd.write(tmp.read(512))
            self.fhnd.write("...\n")
        else:
            self.fhnd.write(tmp.getvalue())
    
    def methodCalled(self, methodName, result_, *args, **kw):
        self._lock_acquire()
        
        self.fhnd = open(self.txtFileName, 'ab', 0)
        
        self.fhnd.write("Counter: %d\n" % self.counter)
        self.fhnd.write("Time: %f\n" % time.time())
        self.fhnd.write("Method: %s\n" % methodName)
        
        self._print("Result:", result_)
        self._print("Args:", args)
        self._print("KW:", kw)
        
        self._printTB()
        
        self.fhnd.write("-------------\n")
        self.fhnd.flush()
        self.fhnd.close()
        
        self.counter += 1
        
        self._lock_release()

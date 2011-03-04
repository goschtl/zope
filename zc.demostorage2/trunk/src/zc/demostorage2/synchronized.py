##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Support for Java-style synchronized methods

Support for synchornized method through a synchronized decorator.

$Id$
"""

class SynchronizedFunction(object):

    def __init__(self, func, lock_name, inst=None):
        self._func = func
        self._lock_name = lock_name
        self._inst = inst

    def __get__(self, inst, class_):
        return self.__class__(self._func, self._lock_name, inst)

    def __call__(self, *args, **kw):
        inst = self._inst
        if inst is None:
            inst = args[0]
            args = args[1:]

        lock = getattr(inst, self._lock_name)
        lock.acquire()
        try:
            return self._func(inst, *args, **kw)
        finally:
            lock.release()

def synchronized(func):
    if isinstance(func, str):
        lock_name = func
        def synchronized(func):
            return SynchronizedFunction(func, lock_name)
        return synchronized
    else:
        return SynchronizedFunction(func, '_lock')


            

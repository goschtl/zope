##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
def all():
    import testTALES
    return testTALES.test_suite()

class harness1:
    def __init__(self):
        self.__callstack = []

    def _assert_(self, name, *args, **kwargs):
        self.__callstack.append((name, args, kwargs))

    def _complete_(self):
        assert len(self.__callstack) == 0, "Harness methods called"

    def __getattr__(self, name):
        cs = self.__callstack
        assert len(cs), 'Unexpected harness method call "%s".' % name
        assert cs[0][0] == name, (
            'Harness method name "%s" called, "%s" expected.' %
            (name, cs[0][0]) )
        return self._method_
        
    def _method_(self, *args, **kwargs):
        name, aargs, akwargs = self.__callstack.pop(0)
        assert aargs == args, "Harness method arguments"
        assert akwargs == kwargs, "Harness method keyword args"

class harness2(harness1):
    def _assert_(self, name, result, *args, **kwargs):
        self.__callstack.append((name, result, args, kwargs))

    def _method_(self, *args, **kwargs):
        name, result, aargs, akwargs = self.__callstack.pop(0)
        assert aargs == args, "Harness method arguments"
        assert akwargs == kwargs, "Harness method keyword args"
        return result
    

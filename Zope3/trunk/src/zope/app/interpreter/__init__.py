##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Code Interpreters Service

$Id: __init__.py,v 1.2 2003/08/21 14:19:24 srichter Exp $
"""
from zope.app.interfaces.interpreter import \
     IGlobalInterpreterService, IInterpreter
from zope.interface import implements


class GlobalInterpreterService:

    implements(IGlobalInterpreterService)

    def __init__(self):
        self.__registry = {}

    def getInterpreter(self, type):
        """See zope.app.interfaces.IInterpreterService"""
        return self.__registry[type]

    def queryInterpreter(self, type, default=None):
        """See zope.app.interfaces.IInterpreterService"""
        return self.__registry.get(type, default)

    def provideInterpreter(self, type, interpreter):
        """See zope.app.interfaces.IGlobalInterpreterService"""
        assert IInterpreter.isImplementedBy(interpreter)
        self.__registry[type] = interpreter
        

interpreterService = GlobalInterpreterService()
provideInterpreter = interpreterService.provideInterpreter
_clear = interpreterService.__init__

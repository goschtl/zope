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
"""Manager for persistent modules associated with a service manager.

$Id: Module.py,v 1.1 2002/10/02 22:18:01 jeremy Exp $
"""

from Persistence import Persistent
from Persistence.Module import PersistentModuleManager
from Persistence.IPersistentModuleManager import IPersistentModuleManager

from Zope.ComponentArchitecture import getServiceManager
from Zope.ContextWrapper import ContextMethod

class Registry:

    # The registry is found via context, but the PersistentModuleManager
    # doesn't know about context.  To make it behave contextually, this
    # Registry class collaborates with Manager to delegate to the
    # registry found via context.

    def __init__(self):
        self._v_manager = None

    def setManager(self, ctx):
        self._v_manager = ctx

    def findModule(self, name):
        return self._v_manager.findModule(name)

    def setModule(self, name, module):
        return self._v_manager.setModule(name, module)

    def delModule(self, name):
        return self._v_manager.delModule(name)

class Manager(Persistent):

    __implements__ = IPersistentModuleManager 

    # The registry for the manager is the ServiceManager.
    # The association between this manager and the registry
    # is static, but the static association can't be stored
    # explicitly in Zope.

    # XXX There is no locking, but every call to setManager() for a
    # particular instance should have the same manager argument.

    # XXX It would be nice if the lookup via getServiceManager()
    # occurred less often.  Best would be to do it only when the
    # object is unpickled.

    def __init__(self):
        self._registry = Registry()
        self._manager = PersistentModuleManager(self._registry)

    def new(self, name, source):
        self._registry.setManager(getServiceManager(self))
        self._manager.new(name, source)

    def update(self, source):
        self._registry.setManager(getServiceManager(self))
        self._manager.update(source)

    def remove(self, source):
        self._registry.setManager(getServiceManager(self))
        self._manager.remove(source)

    new = ContextMethod(new)
    update = ContextMethod(update)
    remove = ContextMethod(remove)

    name = property(lambda self: self._manager.name)
    source = property(lambda self: self._manager.source)

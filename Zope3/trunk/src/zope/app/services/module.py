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

$Id: module.py,v 1.9 2003/06/02 16:24:33 gvanrossum Exp $
"""

from persistence import Persistent
from zodb.code.module import PersistentModuleManager
from zodb.code.interfaces import IPersistentModuleManager
from zodb.code.interfaces import IPersistentModuleImportRegistry
from zodb.code.interfaces import IPersistentModuleUpdateRegistry

from zope.component import getServiceManager
from zope.context import ContextMethod

from zope.interface import implements

from zope.app.fssync.classes import ObjectEntryAdapter, AttrMapping
from zope.app.interfaces.fssync import IObjectFile
from zope.app.interfaces.file import IFileFactory
from zope.app.context import ContextWrapper


class Registry:

    # This is a wrapper around the module service, which is actually
    # the service manager.  The service manager is found via context,
    # but the PersistentModuleManager doesn't know about context.  To
    # make it behave contextually, this Registry class collaborates
    # with the Manager class below to delegate to the registry found
    # via context.

    implements(IPersistentModuleImportRegistry,
               IPersistentModuleUpdateRegistry)

    def __init__(self):
        self._v_module_service = None

    def setModuleService(self, ms):
        # This method is called by methods of Manager below
        self._v_module_service = ms

    # The next three methods are called by the persistent module manager

    def findModule(self, name):
        return self._v_module_service.findModule(name)

    def setModule(self, name, module):
        return self._v_module_service.setModule(name, module)

    def delModule(self, name):
        return self._v_module_service.delModule(name)

    def __getstate__(self):
        # So pickling this object doesn't include the module service
        return {}

class Manager(Persistent):

    implements(IPersistentModuleManager)

    # The registry for the manager is the ServiceManager.
    # The association between this manager and the registry
    # is static, but the static association can't be stored
    # explicitly in Zope.

    # XXX There is no locking, but every call to setModuleService()
    # for a particular instance should have the same manager argument.

    # XXX It would be nice if the lookup via getServiceManager()
    # occurred less often.  Best would be to do it only when the
    # object is unpickled.

    def __init__(self):
        self._registry = Registry()
        self._manager = PersistentModuleManager(self._registry)

    def new(self, name, source):
        self._registry.setModuleService(getServiceManager(self))
        self._manager.new(name, source)

    def update(self, source):
        self._registry.setModuleService(getServiceManager(self))
        self._manager.update(source)

    def remove(self):
        self._registry.setModuleService(getServiceManager(self))
        self._manager.remove()

    new = ContextMethod(new)
    update = ContextMethod(update)
    remove = ContextMethod(remove)

    name = property(lambda self: self._manager.name)
    source = property(lambda self: self._manager.source)


class ModuleAdapter(ObjectEntryAdapter):

    implements(IObjectFile)

    def getBody(self):
        return self.context.source

    def setBody(self, source):
        self.context.update(source)

    def extra(self):
        return AttrMapping(self.context, ("name",))


class ModuleFactory(object):

    implements(IFileFactory)

    def __init__(self, context):
        self.context = context

    def __call__(self, name, content_type, data):
        assert name.endswith(".py")
        name = name[:-3]
        m = Manager()
        m = ContextWrapper(m, self.context)
        m.new(name, data)
        return m

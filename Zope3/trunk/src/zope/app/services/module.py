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

$Id: module.py,v 1.12 2003/06/30 16:25:22 jim Exp $
"""

from persistence import Persistent
from zodb.code.module import PersistentModule, compileModule
from zodb.code.interfaces import IPersistentModuleImportRegistry
from zodb.code.interfaces import IPersistentModuleUpdateRegistry

from zope.interface import implements

from zope.app import zapi
from zope.app.event import function
from zope.app.fssync.classes import ObjectEntryAdapter, AttrMapping
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.fssync import IObjectFile
from zope.app.interfaces.file import IFileFactory
from zope.app.interfaces.services.module import IModuleManager


class Manager(Persistent):

    implements(IModuleManager, IAttributeAnnotatable)

    zapi.ContextAwareDescriptors()

    def __init__(self, name, source):
        self.name = name
        self._source = None
        self.source = source

    def __setstate__(self, state):
        manager = state.get('_manager')
        if manager is None:
            return Persistent.__setstate__(self, state)

        # We need to conver an old-style manager
        self._module = manager._module
        self.name = manager.name
        self._source = manager.source
        self._recompile = False

    def execute(self):
        try:
            mod = self._module
        except AttributeError:
            mod = self._module = PersistentModule(self.name)
        folder = zapi.getWrapperContainer(self)
        compileModule(mod, folder, self.source)
        self._recompile = False

    def getModule(self):
        if self._recompile:
            self.execute()
        return self._module

    def _get_source(self):
        return self._source
    def _set_source(self, source):
        if self._source != source:
            self._source = source
            self._recompile = True
    source = property(_get_source, _set_source)


# Hack to allow unpickling of old Managers to get far enough for __setstate__
# to do it's magic:
Registry = Manager

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
        m = Manager(name, data)
        m = zapi.ContextWrapper(m, self.context)
        m.execute()
        return m


# Installer function that can be called from ZCML.
# This installs an import hook necessary to support persistent modules.

def installPersistentModuleImporter(event):
    from zodb.code.module import PersistentModuleImporter
    PersistentModuleImporter().install()

installPersistentModuleImporter = function.Subscriber(
    installPersistentModuleImporter)

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

$Id: module.py,v 1.17 2003/10/13 16:12:34 fdrake Exp $
"""

from persistence import Persistent
from zodb.code.module import PersistentModule, compileModule
from zope.app.event import function
from zope.app.fssync.classes import ObjectEntryAdapter, AttrMapping
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.file import IFileFactory
from zope.app.interfaces.fssync import IObjectFile
from zope.app.interfaces.services.module import IModuleManager
from zope.interface import implements
from zope.security.proxy import trustedRemoveSecurityProxy
from zope.app.container.contained import Contained

class Manager(Persistent, Contained):

    implements(IModuleManager, IAttributeAnnotatable)

    def __init__(self, name, source):
        self.name = name
        self._source = None
        self.source = source

    def __setstate__(self, state):
        manager = state.get('_manager')
        if manager is None:
            return Persistent.__setstate__(self, state)

        # We need to convert an old-style manager
        self._module = manager._module
        self.name = manager.name
        self._source = manager.source
        self._recompile = False

    def execute(self):
        try:
            mod = self._module
        except AttributeError:
            mod = self._module = PersistentModule(self.name)


        folder = self.__parent__

        # XXX
        # We are currently only supporting trusted code.
        # We don't want the folder to be proxied because, if it is, then
        # the modules will be proxied.
        # When we do support untrusted code, we're going to have to do
        # something different.
        folder = trustedRemoveSecurityProxy(folder)
            
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
        m.__parent__ = self.context
        m.execute()
        return m


# Installer function that can be called from ZCML.
# This installs an import hook necessary to support persistent modules.

def installPersistentModuleImporter(event):
    from zodb.code.module import PersistentModuleImporter
    PersistentModuleImporter().install()

installPersistentModuleImporter = function.Subscriber(
    installPersistentModuleImporter)

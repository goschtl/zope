##############################################################################
#
# Copyright (c) 2002-2005 Zope Corporation and Contributors.
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
"""Module Manager implementation

$Id$
"""
__docformat__ = "reStructuredText"
import persistent
import zodbcode.module
import zope.interface
import zope.component

from zope.filerepresentation.interfaces import IFileFactory
from zope.container.contained import Contained
from zope.app.module.interfaces import IModuleManager
from zope.app.module import ZopeModuleRegistry

class ModuleManager(persistent.Persistent, Contained):

    zope.interface.implements(IModuleManager)

    def __init__(self, source=''):
        # The name is set, once the registration is activated.
        self.name = None
        self._source = None
        self.source = source

    def execute(self):
        """See zope.app.module.interfaces.IModuleManager"""
        try:
            mod = self._module
        except AttributeError:
            mod = self._module = zodbcode.module.PersistentModule(self.name)

        zodbcode.module.compileModule(mod, ZopeModuleRegistry, self.source)
        self._module.__name__ = self.name
        self._recompile = False

    def getModule(self):
        """See zope.app.module.interfaces.IModuleManager"""
        if self._recompile:
            self.execute()
        return self._module

    def _getSource(self):
        return self._source

    def _setSource(self, source):
        if self._source != source:
            self._source = source
            self._recompile = True

    # See zope.app.module.interfaces.IModuleManager
    source = property(_getSource, _setSource)

    def _setName(self, name):
        self.__dict__['name'] = name
        self._recompile = True

    name = property(lambda self: self.__dict__['name'], _setName)
    

class ModuleFactory(object):
    """Special factory for creating module managers in site managment
    folders."""

    zope.interface.implements(IFileFactory)

    def __init__(self, context):
        self.context = context

    def __call__(self, name, content_type, data):
        assert name.endswith(".py")
        name = name[:-3]
        m = ModuleManager(name, data)
        m.__parent__ = self.context
        m.execute()
        return m

@zope.component.adapter(IModuleManager,
                        zope.component.interfaces.IRegistered)
def setNameOnActivation(manager, event):
    """Set the module name upon registration activation."""
    name = event.object.name
    if not isinstance(event.object.name, str):
        # Convert the name to an ascii string to avoid problems with
        # unicode module names
        name = name.encode('ascii', 'ignore')
    manager.name = name

@zope.component.adapter(IModuleManager,
                        zope.component.interfaces.IUnregistered)
def unsetNameOnDeactivation(manager, event):
    """Unset the permission id up registration deactivation."""
    manager.name = None

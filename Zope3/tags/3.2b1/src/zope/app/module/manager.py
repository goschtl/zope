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

from zope.app.container.contained import Contained
from zope.app.filerepresentation.interfaces import IFileFactory
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


def setNameOnActivation(event):
    """Set the module name upon registration activation."""
    module = event.object.component
    if isinstance(module, ModuleManager):
        module.name = event.object.name
        module._recompile = True

def unsetNameOnDeactivation(event):
    """Unset the permission id up registration deactivation."""
    module = event.object.component
    if isinstance(module, ModuleManager):
        module.name = None
        module._recompile = True

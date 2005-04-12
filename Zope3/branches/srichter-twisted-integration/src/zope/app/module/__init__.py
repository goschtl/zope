##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Manager for persistent modules associated with a site manager.

$Id$
"""
__docformat__ = 'restructuredtext'
import sys
import zodbcode.interfaces
import zodbcode.module

from zope.interface import implements
from zope.app import zapi
from zope.app.module.interfaces import IModuleManager


class ZopeModuleRegistry(object):
    """Zope-specific registry of persistent modules.

    This registry is used to lookup local module managers and then get the
    module from them.
    """
    implements(zodbcode.interfaces.IPersistentModuleImportRegistry)

    def findModule(self, name):
        """See zodbcode.interfaces.IPersistentModuleImportRegistry"""
        manager = zapi.queryUtility(IModuleManager, name)
        return manager and manager.getModule() or manager

    def modules(self):
        """See zodbcode.interfaces.IPersistentModuleImportRegistry"""
        return [name
                for name, modulemgr in zapi.getUtilitiesFor(IModuleManager)]

# Make Zope Module Registry a singelton
ZopeModuleRegistry = ZopeModuleRegistry()


def findModule(name, context=None):
    """Find the module matching the provided name."""
    module = ZopeModuleRegistry.findModule(name)
    return module or sys.modules.get(name)

def resolve(name, context=None):
    """Resolve a dotted name to a Python object."""
    pos = name.rfind('.')
    mod = findModule(name[:pos], context)
    return getattr(mod, name[pos+1:], None)


class ZopePersistentModuleImporter(zodbcode.module.PersistentModuleImporter):

    def __init__(self, registry):
        self._registry = registry

    def __import__(self, name, globals={}, locals={}, fromlist=[]):
        mod = self._import(self._registry, name, self._get_parent(globals),
                           fromlist)
        if mod is not None:
            return mod
        return self._saved_import(name, globals, locals, fromlist)


# Installer function that can be called from ZCML.
# This installs an import hook necessary to support persistent modules.
importer = ZopePersistentModuleImporter(ZopeModuleRegistry)

def installPersistentModuleImporter(event):
    importer.install()

def uninstallPersistentModuleImporter(event):
    importer.uninstall()


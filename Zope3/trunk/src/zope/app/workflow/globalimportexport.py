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
"""ProcessDefinition Import Export Utility

$Id: globalimportexport.py,v 1.6 2004/04/15 15:29:45 jim Exp $
"""
__metaclass__ = type

from zope.proxy import removeAllProxies
from zope.interface import implements, providedBy

from zope.app.workflow.interfaces import IProcessDefinition
from zope.app.workflow.interfaces import IGlobalProcessDefinitionImportExport

from StringIO import StringIO

class ImportExportUtility:

    implements(IGlobalProcessDefinitionImportExport)

    def __init__(self):
        self._importers = ImplementorRegistry()
        self._exporters = ImplementorRegistry()

    _clear = __init__

    # IProcessDefinitionImportExport

    def importProcessDefinition(self, context, data):
        """Import a Process Definition
        """
        if not hasattr(data, "read"):
            data = StringIO(data)

        for iface, factory in self._importers.getRegisteredMatching():
            if iface.extends(IProcessDefinition):
                imp = factory()
                data.seek(0)
                if imp.canImport(context, data):
                    data.seek(0)
                    return imp.doImport(context, data)

        raise ValueError, 'No Importer can handle that information'

    def exportProcessDefinition(self, context, process_definition):
        """Export a Process Definition
        """
        clean_pd = removeAllProxies(process_definition)
        interfaces = [x for x in providedBy(clean_pd)
                      if x.extends(IProcessDefinition)]
        for interface in interfaces:
            factory = self._exporters.get(interface)
            if factory is not None:
                return factory().doExport(context, clean_pd)
        raise TypeError, "object doesn't implement IProcessDefinition"


    # IGlobalProcessDefinitionImportExport

    def addImportHandler(self, interface, factory):
        """add Import Handler for ProcessDefinition
        """
        self._importers.register(interface, factory)

    def addExportHandler(self, interface, factory):
        """add Export Handler for ProcessDefinition
        """
        self._exporters.register(interface, factory)


from zope.interface import Interface
class ImplementorRegistry:
    # This was copied from zope.interface.implementor
    # zope.interface.implementor has been removed

    # The implementation that needs this should be rethought

    def __init__(self):
        self._reg = {}

    def _registerAllProvided(self, primary_provide, object, provide):
        # Registers a component using (require, provide) as a key.
        # Also registers superinterfaces of the provided interface,
        # stopping when the registry already has a component
        # that provides a more general interface or when the Base is Interface.

        reg = self._reg
        reg[provide] = (primary_provide, object)
        bases = getattr(provide, '__bases__', ())
        for base in bases:
            if base is Interface:
                # Never register the say-nothing Interface.
                continue
            existing = reg.get(base, None)
            if existing is not None:
                existing_provide = existing[0]
                if existing_provide is not primary_provide:
                    if not existing_provide.extends(primary_provide):
                        continue
                    # else we are registering a general component
                    # after a more specific component.
            self._registerAllProvided(primary_provide, object, base)


    def register(self, provide, object):
        self._registerAllProvided(provide, object, provide)


    def getRegisteredMatching(self):
        return [(iface, impl)
                for iface, (regiface, impl) in self._reg.items()
                if iface is regiface]

    def get(self, interface, default=None):
        c = self._reg.get(interface)
        if c is not None:
            return c[1]

        return default

globalImportExport = ImportExportUtility()


_clear = globalImportExport._clear

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp

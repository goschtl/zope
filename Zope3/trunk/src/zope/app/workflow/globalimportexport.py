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

$Id: globalimportexport.py,v 1.1 2003/05/08 17:27:18 jack-e Exp $
"""
__metaclass__ = type

from zope.interface.implementor import ImplementorRegistry
from zope.interface._flatten import _flatten
from zope.proxy.introspection import removeAllProxies
from zope.app.interfaces.workflow import IProcessDefinition
from zope.app.interfaces.workflow import IGlobalProcessDefinitionImportExport

from StringIO import StringIO

class ImportExportUtility:

    __implements__ = IGlobalProcessDefinitionImportExport


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
        interfaces = filter(lambda x: x.extends(IProcessDefinition),
                           _flatten(clean_pd.__implements__))
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

    

globalImportExport = ImportExportUtility()


_clear = globalImportExport._clear

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp

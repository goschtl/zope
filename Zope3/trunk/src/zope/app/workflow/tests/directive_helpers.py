##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

__metaclass__ = type

from zope.app.interfaces.workflow import IProcessDefinition
from zope.app.interfaces.workflow import IGlobalProcessDefinitionImportExport
from zope.app.interfaces.workflow import IProcessDefinitionImportHandler
from zope.app.interfaces.workflow import IProcessDefinitionExportHandler



class ITestProcessDefinitionA(IProcessDefinition):
    pass

class ITestProcessDefinitionB(IProcessDefinition):
    pass


class TestImportHandlerA:

    __implements__ = IProcessDefinitionImportHandler

    def canImport(self, context, data):
        return bool(data.read() == 'A')

    def doImport(self, context, data):
        return 'Imported A'


class TestImportHandlerB:

    __implements__ = IProcessDefinitionImportHandler

    def canImport(self, context, data):
        return bool(data.read() == 'B')

    def doImport(self, context, data):
        return 'Imported B'



class TestExportHandlerA:

    __implements__ = IProcessDefinitionExportHandler

    def doExport(self, context, process_definition):
        return 'Exported A'


class TestExportHandlerB:

    __implements__ = IProcessDefinitionExportHandler

    def doExport(self, context, process_definition):
        return 'Exported B'

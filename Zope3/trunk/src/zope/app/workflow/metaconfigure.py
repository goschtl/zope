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

$Id: metaconfigure.py,v 1.1 2003/05/08 17:27:18 jack-e Exp $
"""
__metaclass__ = type

from zope.configuration.action import Action
from globalimportexport import globalImportExport

#

def importHandlerDirective(_context, interface, factory):
    interface = _context.resolve(interface)
    factory = _context.resolve(factory)
    return [
        Action(
              discriminator = ('workflow','importHandler', interface),
              callable = addImportHandler,
              args = (interface, factory)
              )
        ]


def exportHandlerDirective(_context, interface, factory):
    interface = _context.resolve(interface)
    factory = _context.resolve(factory)
    return [
        Action(
              discriminator = ('workflow','exportHandler', interface),
              callable = addExportHandler,
              args = (interface, factory)
              )
        ]




def addImportHandler(interface, factory):
    globalImportExport.addImportHandler(interface, factory)

def addExportHandler(interface, factory):
    globalImportExport.addExportHandler(interface, factory)


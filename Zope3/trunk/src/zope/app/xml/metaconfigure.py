##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Configuration directive for defining XML schema based interface.

$Id: metaconfigure.py,v 1.2 2003/04/10 16:07:45 philikon Exp $
"""

from zope.app.xml.schemainterface import XMLSchemaInterfaceClass
from zope.app.component.globalinterfaceservice import interfaceService

def schemaInterface(_context, uri):
    schema_interface = XMLSchemaInterfaceClass(uri)
    # XXX normally we would return an Action here, but then the interface would
    # not be resolvable if other configuration directives make references to it
    interfaceService.provideInterface(uri, schema_interface)
    return []

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

$Id: metaconfigure.py,v 1.1 2003/04/09 20:51:33 philikon Exp $
"""

from zope.interface.interface import InterfaceClass
from zope.app.interfaces.xml.representable import IXMLRepresentable
from zope.app.component.globalinterfaceservice import interfaceService

def schemaInterface(_context, uri):
    doc = """XML Schema based interface

    Instances of this interface must be XML representable with XML that conforms
    to the schema: %s""" % uri
    schema_interface = InterfaceClass(uri, (IXMLRepresentable,),
                                      {'__doc__': doc})
    # XXX normally we would return an Action here, but then the interface would
    # not be resolvable if other configuration directives make references to it
    interfaceService.provideInterface(uri, schema_interface)
    return []

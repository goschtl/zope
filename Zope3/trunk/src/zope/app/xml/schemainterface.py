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
"""XML schema interfaces

$Id: schemainterface.py,v 1.1 2003/04/10 16:07:45 philikon Exp $
"""

from zope.interface.interface import InterfaceClass
from zope.app.interfaces.xml.representable import IXMLRepresentable

class XMLSchemaInterfaceClass(InterfaceClass):
    """
    Class for XML schema interfaces
    """

    __safe_for_unpickling__ = True
    
    def __init__(self, uri):
        doc = """XML Schema based interface

    Instances of this interface must be XML representable with XML that conforms
    to the schema: %s""" % uri
        super(XMLSchemaInterfaceClass, self).__init__(uri, (IXMLRepresentable,),
                                                      __doc__=doc)

    def __reduce__(self):
        return (XMLSchemaInterfaceClass, (self.getName(),))

    #
    # Identity comparison does not work with security proxies. Therefore we
    # override the default equality comparison (which does identity comparison).
    #

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__name__ == other.__name__)

    def __hash__(self):
        return hash(self.__name__)

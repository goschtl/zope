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
"""'xml' namespace directives schema 

$Id: metadirectives.py,v 1.1 2003/08/01 20:18:05 srichter Exp $
"""
from zope.configuration.fields import URI
from zope.interface import Interface

class ISchemaInterfaceDirective(Interface):
    """This directive creates an interface from an XML Schema definition,
    which is specifed by the URI."""

    uri = URI(
        title=u"URI",
        description=u"Specifies the URI of the XML Schema.",
        required=True)

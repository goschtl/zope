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
"""

Revision information: $Id: xmlrpcviews.py,v 1.2 2002/12/25 14:15:19 jim Exp $
"""

from zope.interface import Interface
from zope.publisher.interfaces.xmlrpc import IXMLRPCPublisher

class IC(Interface): pass

class V1:
    __implements__ = IXMLRPCPublisher

    def __init__(self, context, request):
        self.context = context
        self.request = request

class VZMI(V1):
    pass

class R1:
    def __init__(self, request):
        self.request = request

    __implements__ = IXMLRPCPublisher

class RZMI(R1):
    pass

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
"""XML-RPC Publisher Components

This module contains the MethodPublisher, and XMLRPCView.

$Id$
"""
from zope.component.interfaces import IView
from zope.component.interfaces import IPresentation

class IXMLRPCPresentation(IPresentation):
    """XML-RPC presentation
    """

class IXMLRPCView(IXMLRPCPresentation, IView):
    """XMLRPC View"""

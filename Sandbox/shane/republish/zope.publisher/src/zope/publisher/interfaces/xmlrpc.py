##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""XML-RPC interfaces

$Id: browser.py 96546 2009-02-14 20:48:37Z shane $
"""

from zope.publisher.interfaces.base import IPublishTraverse
from zope.publisher.interfaces.http import IHTTPRequest

class IXMLRPCRequest(IHTTPRequest):
    """XML-RPC Request
    """

class IXMLRPCPublisher(IPublishTraverse):
    """XML-RPC-specific traversal"""

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
"""

$Id: unauthorized.py,v 1.1 2003/03/29 17:03:59 sidnei Exp $
"""
__metaclass__ = type

from zope.app.interfaces.http import IHTTPException

class Unauthorized:

    __implements__ = IHTTPException

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.request.unauthorized("basic realm='Zope'")
        return ''

    __str__ = __call__

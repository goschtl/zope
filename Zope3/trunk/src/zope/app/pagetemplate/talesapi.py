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
"""Implementation of the Zope TALES API


$Id: talesapi.py,v 1.1 2003/04/15 18:52:57 matth Exp $
"""

from zope.app.interfaces.talesapi import IZopeTalesAPI
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.component import queryAdapter

class ZopeTalesAPI(object):

    __implements__ = IZopeTalesAPI

    def __init__(self, context):
        self.context = context

    def title(self):
        a = queryAdapter(self.context, IZopeDublinCore)
        if a is None:
            raise AttributeError, 'title'
        return a.title

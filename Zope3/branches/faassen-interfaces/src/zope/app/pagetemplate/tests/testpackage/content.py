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
"""Test Content

$Id: content.py,v 1.4 2003/08/21 14:19:28 srichter Exp $
"""
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class Content:
    def getSomething(self):
        return 42


class PTComponent(object):
    def __init__(self, content, request=None):
        self.context = content
        self.request = request

    index = ViewPageTemplateFile("view.pt")
    default = ViewPageTemplateFile("default.pt")
    nothing = ViewPageTemplateFile("nothing.pt")

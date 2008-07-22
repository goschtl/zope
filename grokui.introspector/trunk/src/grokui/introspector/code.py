##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Introspecting code.
"""
import grok
from zope.introspector.code import Code, PackageOrModule

class Index(grok.View):
    grok.context(Code)
    def render(self):
        return "This is code"

class CodeTraverser(grok.Traverser):
    grok.context(PackageOrModule)

    def traverse(self, name):
        try:
            return self.context[name]
        except KeyError:
            return None


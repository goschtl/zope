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
"""Provide description objects for arbitrary objects.
"""
import grokcore.component as grok
from zope.introspector.interfaces import IObjectDescriptionProvider

descriptor_registry = []

class DescriptionFinder(grok.GlobalUtility):
    grok.implements(IObjectDescriptionProvider)

    def getDescription(obj_or_dotted_path, *args, **kw):
        pass

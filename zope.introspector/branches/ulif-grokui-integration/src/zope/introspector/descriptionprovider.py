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
from zope.introspector.interfaces import (IObjectDescriptionProvider,
                                          IObjectInfo)
from zope.introspector.objectinfo import ObjectInfo
from zope.introspector.util import resolve

# The descriptor provider registry
descriptor_registry = []

class DescriptionFinder(grok.GlobalUtility):
    """Find a description provider.

    Find a component that takes an object or a dotted name and returns
    some kind of info object to describe it.
    """
    grok.implements(IObjectDescriptionProvider)

    def getDescription(self, obj=None, dotted_name=None, **kw):
        if obj is None and dotted_name is not None:
            obj = resolve(dotted_name)
        sorted_reg = sorted(descriptor_registry,
                            cmp = lambda x,y: x['priority'] - y['priority'])
        for descriptor in sorted_reg:
            
            handler = descriptor['handler']()
            if handler.canHandle(obj, dotted_name=dotted_name):
                return handler.getDescription(obj, dotted_name=dotted_name)
        # If no descriptor could be found, we return the plainest one.
        return ObjectInfo(obj, dotted_name=dotted_name)

class DescriptionProvider(object):
    """Description Providers must inherit from this to be registered.
    """
    def canHandle(self, obj, dotted_name=None, **kw):
        return False

    def getDescription(self, obj, dotted_name=None, **kw):
        return ObjectInfo(obj, dotted_name)


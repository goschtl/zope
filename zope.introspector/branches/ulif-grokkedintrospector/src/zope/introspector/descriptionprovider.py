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
import martian
from zope.introspector.interfaces import (IObjectDescriptionProvider,
                                          IObjectInfo)

descriptor_registry = []

class DescriptionFinder(grok.GlobalUtility):
    grok.implements(IObjectDescriptionProvider)

    def getDescription(self, obj_or_dotted_path, *args, **kw):
        for descriptor in descriptor_registry:
            handler = descriptor['handler']
            if handler.canHandle(obj_or_dotted_path):
                return handler.getDescription(obj_or_dotted_path)
        # If no descriptor could be found, we return the plainest one.
        return ObjectInfo(obj_or_dotted_path)

class DescriptionProvider(object):
    pass

class DescriptionProviderGrokker(martian.ClassGrokker):
    """Grok descriptor providers.

    Groks classes derived from ``DescriptorProvider`` on startup and
    adds them to the local descriptor registry.
    """
    martian.component(DescriptionProvider)

    def execute(self, obj=None, *args, **kw):
        name = getattr(obj, 'name', '')
        descriptor_registry.insert(0, dict(name=name, handler=obj()))
        return True

module_grokker = martian.ModuleGrokker()
module_grokker.register(DescriptionProviderGrokker())


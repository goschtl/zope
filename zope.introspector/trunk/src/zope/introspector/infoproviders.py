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
import inspect
import martian
from zope.introspector.meta import priority
from zope.introspector.descriptionprovider import DescriptionProvider
from zope.introspector.interfaces import IObjectInfo
from zope.introspector.objectinfo import ObjectInfo, PackageInfo

class SimpleDescriptionProvider(DescriptionProvider):
    name = 'simple'
    priority(1001)
    def getDescription(self, obj, dotted_name=None, **kw):
        return ObjectInfo(obj, dotted_name=dotted_name)

    def canHandle(self, obj, dotted_name=None, **kw):
        return True


class PackageDescriptionProvider(DescriptionProvider):
    name = 'package'
    priority(1000)
    def getDescription(self, obj, **kw):
        return PackageInfo(obj)

    def canHandle(self, obj=None, dotted_name=None, **kw):
        if not inspect.ismodule(obj):
            return False
        info = martian.scan.module_info_from_module(obj)
        return info.isPackage()

##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""Support for non-versioned data embedded in versioned objects.

$Id$
"""
import zope.interface

from zope.app.versioncontrol.interfaces import INonVersionedData, IVersionable

def isAVersionableResource(object):
    return IVersionable.providedBy(object)


try:
    # Optional support for references.
    from Products.References.Proxy import proxyBase
    from Products.References.PathReference import PathReference
except ImportError:
    isProxyOrReference = None
else:
    def isProxyOrReference(obj):
        if proxyBase(obj) is not obj:
            return 1
        if isinstance(obj, PathReference):
            return 1
        return 0


def listNonVersionedObjects(obj):
    return INonVersionedData(obj).listNonVersionedObjects()

def getNonVersionedData(obj):
    return INonVersionedData(obj).getNonVersionedData()

def removeNonVersionedData(obj):
    INonVersionedData(obj).removeNonVersionedData()

def restoreNonVersionedData(obj, dict):
    INonVersionedData(obj).restoreNonVersionedData(dict)



class StandardNonVersionedDataAdapter:
    """Non-versioned data adapter for arbitrary things.
    """
    zope.interface.implements(INonVersionedData)

    attrs = ()

    def __init__(self, obj):
        self.obj = obj

    def listNonVersionedObjects(self):
        # Assume it's OK to clone all of the attributes.
        # They will be removed later by removeNonVersionedData.
        return ()

    def removeNonVersionedData(self):
        for attr in self.attrs:
            try:
                delattr(self.obj, attr)
            except AttributeError:
                pass

    def getNonVersionedData(self):
        data = {}
        for attr in self.attrs:
            if hasattr(self.obj, attr):
                data[attr] = getattr(self.obj), attr
        return data

    def restoreNonVersionedData(self, data):
        for attr in self.attrs:
            if data.has_key(attr):
                setattr(self.obj, attr, data[attr])

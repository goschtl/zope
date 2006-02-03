##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""extrinsic references

$Id$
"""
import persistent
from BTrees import OOBTree

from zope import interface
from zope.app.keyreference.interfaces import IKeyReference
from zope.app.component.interfaces import ILocalUtility

from zc.extrinsicreference.interfaces import IExtrinsicReferences

class ExtrinsicReferences(persistent.Persistent):

    interface.implements(IExtrinsicReferences, ILocalUtility)

    # To be usable as an ILocalUtility we have to have these.
    __parent__ = __name__ = None

    def __init__(self):
        self.references = OOBTree.OOBTree()

    def add(self, obj, value):
        key = IKeyReference(obj)
        refs = self.references.get(key)
        if refs is None:
            refs = self.references[key] = OOBTree.OOTreeSet()
        refs.insert(IKeyReference(value))

    def update(self, obj, values):
        key = IKeyReference(obj)
        refs = self.references.get(key)
        if refs is None:
            refs = self.references[key] = OOBTree.OOTreeSet()
        refs.update(IKeyReference(v) for v in values)

    def remove(self, obj, value):
        key = IKeyReference(obj)
        refs = self.references.get(key)
        if refs is not None:
            refs.remove(IKeyReference(value)) # raises KeyError when we desire
        else:
            raise KeyError("Object and value pair does not exist")

    def discard(self, obj, value):
        try:
            self.remove(obj, value)
        except KeyError:
            pass

    def contains(self, obj, value):
        key = IKeyReference(obj)
        refs = self.references.get(key)
        if refs is not None:
            return IKeyReference(value) in refs
        return False

    def set(self, obj, values):
        key = IKeyReference(obj)
        refs = self.references.get(key)
        vals = [IKeyReference(v) for v in values]
        if not vals:
            if refs is not None:
                # del
                del self.references[key]
        else:
            if refs is None:
                refs = self.references[key] = OOBTree.OOTreeSet()
            else:
                refs.clear()
            refs.update(vals)

    def get(self, obj):
        key = IKeyReference(obj)
        refs = self.references.get(key, ())
        for kr in refs:
            yield kr()

# TODO these belong elsewhere (zc.shortcut, maybe?)
from zope.app import zapi
from zc.shortcut.interfaces import IShortcut

def registerShortcut(shortcut, event):
    """Subscriber to add an extrinsic reference."""
    registry = zapi.queryUtility(IExtrinsicReferences, 'shortcuts')
    if registry is not None:
        # We use raw_target because we don't want a proxy.
        registry.add(shortcut.raw_target, shortcut)

def unregisterShortcut(shortcut, event):
    """Subscriber to remove an extrinsic reference."""
    registry = zapi.queryUtility(IExtrinsicReferences, 'shortcuts')
    if registry is not None:
        # We use raw_target because we don't want a proxy.
        registry.discard(shortcut.raw_target, shortcut)

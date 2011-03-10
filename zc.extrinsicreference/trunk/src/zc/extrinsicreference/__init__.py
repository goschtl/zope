##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Extrinsic references implementation"""

from zc.extrinsicreference.interfaces import IExtrinsicReferences
import BTrees
import persistent
import zope.app.keyreference.interfaces
import zope.component
import zope.interface


class ExtrinsicReferences(persistent.Persistent):

    zope.interface.implements(IExtrinsicReferences)

    # To be usable as an ILocalUtility we have to have these.
    __parent__ = __name__ = None

    def __init__(self):
        self.references = BTrees.OOBTree.OOBTree()

    def add(self, obj, value):
        key = zope.app.keyreference.interfaces.IKeyReference(obj)
        refs = self.references.get(key)
        if refs is None:
            refs = self.references[key] = BTrees.OOBTree.OOTreeSet()
        refs.insert(zope.app.keyreference.interfaces.IKeyReference(value))

    def update(self, obj, values):
        key = zope.app.keyreference.interfaces.IKeyReference(obj)
        refs = self.references.get(key)
        if refs is None:
            refs = self.references[key] = BTrees.OOBTree.OOTreeSet()
        refs.update(zope.app.keyreference.interfaces.IKeyReference(v)
            for v in values)

    def remove(self, obj, value):
        key = zope.app.keyreference.interfaces.IKeyReference(obj)
        refs = self.references.get(key)
        if refs is not None:
            # raises KeyError when the value isn't found
            refs.remove(zope.app.keyreference.interfaces.IKeyReference(value))
        else:
            raise KeyError("Object and value pair does not exist")

    def discard(self, obj, value):
        try:
            self.remove(obj, value)
        except KeyError:
            pass

    def contains(self, obj, value):
        key = zope.app.keyreference.interfaces.IKeyReference(obj)
        refs = self.references.get(key)
        if refs is not None:
            return zope.app.keyreference.interfaces.IKeyReference(value) in refs
        return False

    def set(self, obj, values):
        key = zope.app.keyreference.interfaces.IKeyReference(obj)
        refs = self.references.get(key)
        vals = map(zope.app.keyreference.interfaces.IKeyReference, values)
        if not vals:
            if refs is not None:
                # del
                del self.references[key]
        else:
            if refs is None:
                refs = self.references[key] = BTrees.OOBTree.OOTreeSet()
            else:
                refs.clear()
            refs.update(vals)

    def get(self, obj):
        key = zope.app.keyreference.interfaces.IKeyReference(obj)
        refs = self.references.get(key, ())
        for kr in refs:
            yield kr()


def registerShortcut(shortcut, event):
    """Subscriber to add an extrinsic reference."""
    registry = zope.component.queryUtility(IExtrinsicReferences, 'shortcuts')
    if registry is not None:
        # We use raw_target because we don't want a proxy.
        registry.add(shortcut.raw_target, shortcut)

def unregisterShortcut(shortcut, event):
    """Subscriber to remove an extrinsic reference."""
    registry = zope.component.queryUtility(IExtrinsicReferences, 'shortcuts')
    if registry is not None:
        # We use raw_target because we don't want a proxy.
        registry.discard(shortcut.raw_target, shortcut)

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

import zope.interface

class IExtrinsicReferences(zope.interface.Interface):
    """An object that stores extrinsic references to another object

    All objects must be adaptable to
    zope.app.keyreference.interfaces.IKeyReference."""

    def add(obj, value):
        """Add an object and an associated value to the registry.

        Both object and value must be adaptable to IKeyReference.

        Multiple values may be stored for a single key.  Each value is
        only stored once; comparisons are performed using the value's
        IKeyReference hash.
        """

    def update(obj, values):
        """For given object, add all values in iterable values.

        Object and each value must be adaptable to IKeyReference.  Identical
        values (as determined by IKeyReference) are collapsed to a single
        instance (so, for instance, a set of [A, B, B, C, B] will be
        collapsed to a logical set of A, B, C).
        """

    def get(obj):
        """Retrieve an iterable of the values associated with the object.

        If there are no references for `obj`, an iterable with no entries is
        returned.
        """

    def remove(obj, value):
        """Remove the specified value associated with the object.

        Comparisons are made with the IKeyReference hashes.

        If `value` is not set for `obj`, raises KeyError.
        """

    def contains(obj, value):
        """returns a boolean value of whether the obj : value pair exists."""

    def discard(obj, value):
        """Remove the specified value associated with the object.

        Comparisons are made with the IKeyReference hashes.

        If `value` is not set for `obj`, silently ignores.
        """

    def set(obj, values):
        """Set the values for obj to the values in the given iterable.

        Replaces any previous values for obj.  Object and each value must be
        adaptable to IKeyReference.  Identical values (as determined by
        IKeyReference) are collapsed to a single instance (so, for instance,
        values of [A, B, B, C, B] will be collapsed to a logical set of
        A, B, C).

        Setting an empty values is the canonical way of clearing values for an
        object.
        """

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
"""

$Id: annotation.py,v 1.2 2002/12/25 14:12:56 jim Exp $
"""

from zope.interface import Interface
from zope.interface import Attribute


class IAnnotatable(Interface):
    """
    Marker interface for objects that support storing annotations.

    This interface says "There exists an adapter to an IAnnotations
    for an object that implements IAnnotatable".

    Classes should not directly declare that they implement this interface.
    Instead they should implement an interface derived from this one, which
    details how the annotations are to be stored, such as
    IAttributeAnnotatable.
    """


class IAnnotations(IAnnotatable):
    """
    Annotations store arbitrary application data under package unique keys
    """

    def __getitem__(key):
        """
        Return the annotation stored under key.

        Raises KeyError if key not found.
        """

    def get(key, default=None):
        """
        Return the annotation stored under key, returning default if not found.
        """

    def __setitem__(key, memento):
        """
        Store annotation under key.

        In order to avoid key collisions, users of this interface must
        use their dotted package name as part of the key name.
        """

    def __delitem__(key):
        """
        Removes the annotation stored under key.

        Raises a KeyError if the key is not found.
        """


class IAttributeAnnotatable(IAnnotatable):
    """
    Marker interface giving permission for an IAnnotations adapter to store
    data in an attribute named __annotations__.
    """

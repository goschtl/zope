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

$Id: IAnnotations.py,v 1.2 2002/06/10 23:27:51 jim Exp $
"""
from IAnnotatable import IAnnotatable
from Interface import Interface

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

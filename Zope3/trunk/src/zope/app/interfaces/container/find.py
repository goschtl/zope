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

$Id: find.py,v 1.2 2002/12/25 14:12:58 jim Exp $
"""

from zope.interface import Interface

class IFind(Interface):
    """
    Find support for containers.
    """

    def find(id_filters=None, object_filters=None):
        """Find object that matches all filters in all sub objects,
        not including this container itself.
        """

class IObjectFindFilter(Interface):

    def matches(object):
        """Returns true if the object matches the filter criteria.
        """

class IIdFindFilter(Interface):

    def matches(id):
        """Returns true if the id matches the filter criteria.
        """

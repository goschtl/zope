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

Revision information:
$Id: IEventSet.py,v 1.2 2002/06/10 23:29:25 jim Exp $
"""

from Interface import Interface

class IEventSet(ISubscriber):
    """An unordered collection of location-independent events."""

    def size():
        """Returns the number of events stored."""

    def get(n=None):
        """Returns a collection of events.

        This must be iteratable.
        """

##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Interfaces for apelib.zodb3.

$Id$
"""

from Interface import Interface


class IResourceAccess (Interface):
    """Provides access to a resource that may need periodic updates.
    """

    def access(consumer):
        """Returns the resource.
        """

    def release(consumer):
        """Indicates the given consumer is finished with the resource.

        The implementation may take an opportunity to update the resource.
        """


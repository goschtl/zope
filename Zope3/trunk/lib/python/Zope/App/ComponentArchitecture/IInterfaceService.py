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
$Id: IInterfaceService.py,v 1.3 2002/12/04 09:54:04 jim Exp $
"""

from Interface import Interface

class IInterfaceService(Interface):
    """Service that keeps track of used interfaces
    """

    def getInterface(id):
        """Return the interface registered for the given id

        A ComponentLookupError is raised if the interface can't be found.
        """

    def queryInterface(id, default=None):
        """Return the interface registered for the given id

        The default is returned if the interface can't be found.
        """

    def searchInterface(search_string):
        """Return the interfaces that match the search string.
        """

    def searchInterfaceIds(search_string):
        """Return the ids of the interfaces that match the search string.
        """


__doc__ = IInterfaceService.__doc__ + __doc__

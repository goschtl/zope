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
$Id: interfaceservice.py,v 1.1 2003/04/09 16:35:06 philikon Exp $
"""

from zope.interface import Interface

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

    def searchInterface(search_string='', base=None):
        """Return the interfaces that match the search criteria

        If a search string is given, only interfaces that contain the
        string in their documentation will be returned.

        If base is given, only interfaces that equal or extend base
        will be returned.

        """

    def searchInterfaceIds(search_string='', base=None):
        """Return the ids of the interfaces that match the search criteria.

        See searchInterface

        """

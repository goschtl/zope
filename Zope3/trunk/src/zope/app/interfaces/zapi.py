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
"""Interface definition for the Zope convenience API module

$Id: zapi.py,v 1.9 2003/09/21 17:32:26 jim Exp $
"""
from zope.component.interfaces import IComponentArchitecture
from zope.app.interfaces.traversing import ITraversalAPI

class IZAPI(
    IComponentArchitecture,
    ITraversalAPI,
    ):
    """Convenience API for use with Zope applications.
    """

    def name(obj):
        """Return an object's name

        This is the name the object is stored under in the container
        it was accessed in.  If the name is unknown, None is returned.
        """

    def UserError(*args):
        """Return an error message to a user.

        The error is an exception to be raised.

        The given args will be converted to strings and displayed in
        the message shown the user.
        """

    def add(container, name, object):
        """Add an object to a container

        This helper function takes care of getting an adapter that
        publishes necessary errors and calling necessary hooks.
        
        """

    def remove(container, name):
        """Remove an object from a container

        This helper function takes care of getting an adapter that
        publishes necessary errors and calling necessary hooks.
        
        """

        

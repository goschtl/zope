##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
$Id: IObjectEntry.py,v 1.2 2002/10/11 06:28:05 jim Exp $
"""

from Interface import Interface

class IObjectEntry(Interface):
    """File-system object representation
    """

    def extra():
        """Return extra data for the entry.

        The data are returned as a mapping object that allows *both*
        data retrieval and setting.  The mapping is from names to
        objects that will be serialized to or from the file system.

        """

    def typeIdentifier():
        """Return a dotted name that identifies the object type.

        This is typically a dotted class name.

        This is used when synchronizing from the file system to the
        database to decide whether the existing object and the new
        object are of the same type.
        
        """

    def factory():
        """Return the dotted name of a factory to recreate an empty entry.

        The factory will be called with no arguments. It is usually
        the dotted name of the object class.
        
        """

__doc__ = IObjectEntry.__doc__ + __doc__

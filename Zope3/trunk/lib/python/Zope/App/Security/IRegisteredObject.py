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
"""Things that can be registered in a Registry."""

from Interface import Interface

class IRegisteredObject(Interface):
    def getId():
        """Get the id of the registered object."""

    def getTitle():
        """Get the human readable title of the registered object.
        Must be a string, but it may be empty.
        """

    def getDescription():
        """Get the human readable description of the registered object.
        Must be a string, but it may be empty.
        """

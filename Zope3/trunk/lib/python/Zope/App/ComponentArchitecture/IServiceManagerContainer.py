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

$Id: IServiceManagerContainer.py,v 1.2 2002/10/04 17:41:12 jim Exp $
"""

from Interface import Interface

class IReadServiceManagerContainer(Interface):

    def getServiceManager():
        """Returns the service manager contained in this object.

        If there isn't a service manager, raise a component lookup.
        """

    def queryServiceManager(default=None):
        """Returns the service manager contained in this object.

        If there isn't a service manager, return the default.
        """

    def hasServiceManager():
        """Query to find out if the component defines a service manager."""

Read = IReadServiceManagerContainer

class IWriteServiceManagerContainer(Interface):

    def setServiceManager(sm):
        """Sets the service manager for this object."""

Write = IWriteServiceManagerContainer

class IServiceManagerContainer(IReadServiceManagerContainer,
                               IWriteServiceManagerContainer):
    pass


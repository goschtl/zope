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
$Id: servertyperegistry.py,v 1.2 2003/06/25 15:29:32 fdrake Exp $
"""
from zope.app.interfaces.startup.simpleregistry import ISimpleRegistry
from zope.app.process.servertype import IServerType
from zope.app.process.simpleregistry import SimpleRegistry
from zope.interface import implements


class IServerTypeRegistry(ISimpleRegistry):
    """
    The ServerType Registry manages a list of all the fields
    available in Zope. A registry is useful at this point, since
    fields can be initialized and registered by many places.

    Note that it does not matter whether we have classes or instances as
    fields. If the fields are instances, they must implement
    IInstanceFactory.
    """


class ServerTypeRegistry(SimpleRegistry):
    """Registry for the various Server types"""
    implements(IServerTypeRegistry)


ServerTypeRegistry = ServerTypeRegistry(IServerType)
registerServerType = ServerTypeRegistry.register
getServerType = ServerTypeRegistry.get

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
$Id: requestfactoryregistry.py,v 1.2 2002/12/25 14:13:24 jim Exp $
"""
from zope.app.interfaces.startup.simpleregistry import ISimpleRegistry
from zope.app.startup.simpleregistry import SimpleRegistry
from zope.app.startup.requestfactory import IRequestFactory


class IRequestFactoryRegistry(ISimpleRegistry):
    """
    The RequestFactory Registry manages a list of all the fields
    available in Zope. A registry is useful at this point, since
    fields can be initialized and registered by many places.

    Note that it does not matter whether we have classes or instances as
    fields. If the fields are instances, they must implement
    IInstanceFactory.
    """


class RequestFactoryRegistry(SimpleRegistry):
    __implements__ =  (IRequestFactoryRegistry,)


RequestFactoryRegistry = RequestFactoryRegistry(IRequestFactory)
registerRequestFactory = RequestFactoryRegistry.register
getRequestFactory = RequestFactoryRegistry.get

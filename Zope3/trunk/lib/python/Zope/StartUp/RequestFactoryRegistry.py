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

$Id: RequestFactoryRegistry.py,v 1.2 2002/06/10 23:29:43 jim Exp $
"""


from Zope.App.Formulator.SimpleRegistry import SimpleRegistry
from Zope.App.Formulator.ISimpleRegistry import ISimpleRegistry
from RequestFactory import IRequestFactory 

class IRequestFactoryRegistry(ISimpleRegistry):
    """
    The RequestFactory Registry manages a list of all the fields
    available in Zope. A registry is useful at this point, since
    fields can be initialized and registered by many places.

    Note that it does not matter whether we have classes or instances as
    fields. If the fields are instances, they must implement
    IInstanceFactory.
    """
    pass


class RequestFactoryRegistry(SimpleRegistry):
    """ """

    __implements__ =  (IRequestFactoryRegistry,)



RequestFactoryRegistry = RequestFactoryRegistry(IRequestFactory)
registerRequestFactory = RequestFactoryRegistry.register
getRequestFactory = RequestFactoryRegistry.get

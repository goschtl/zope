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
"""ServiceManagerContainer implementation.

$Id: servicecontainer.py,v 1.4 2003/06/11 17:44:34 gvanrossum Exp $
"""

from zope.component.exceptions import ComponentLookupError
from zope.app.interfaces.services.service import IServiceManagerContainer
from zope.component.interfaces import IServiceService
from zope.interface import implements

class ServiceManagerContainer:

    """Implement access to the service manager (++etc++site).

    This is a mix-in that implements the IServiceManagerContainer
    interface; for example, it is used by the Folder implementation.
    """

    implements(IServiceManagerContainer)

    __sm = None

    def hasServiceManager(self):
        return self.__sm is not None

    def getServiceManager(self):
        if self.__sm is not None:
            return self.__sm
        else:
            raise ComponentLookupError('no service manager defined')

    def queryServiceManager(self, default=None):
        if self.__sm is not None:
            return self.__sm
        else:
            return default

    def setServiceManager(self, sm):
        if IServiceService.isImplementedBy(sm):
            self.__sm = sm
        else:
            raise ValueError('setServiceManager requires an IServiceService')

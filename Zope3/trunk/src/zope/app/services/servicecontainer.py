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

from zope.component.exceptions import ComponentLookupError
from zope.app.interfaces.services.service import IServiceManagerContainer  
from zope.component.interfaces import IServiceService

class ServiceManagerContainer:

    __implements__ =  IServiceManagerContainer

    def hasServiceManager(self):
        '''See interface IReadServiceManagerContainer'''
        return hasattr(self, '_ServiceManagerContainer__sm')

    def getServiceManager(self):
        '''See interface IReadServiceManagerContainer'''

        try:
            return self.__sm
        except AttributeError:
            raise ComponentLookupError('no service manager defined')

    def queryServiceManager(self, default=None):
        '''See interface IReadServiceManagerContainer'''

        return getattr(self, '_ServiceManagerContainer__sm', default)

    def setServiceManager(self, sm):
        '''See interface IWriteServiceManagerContainer'''

        if IServiceService.isImplementedBy(sm):
            self.__sm = sm
        else:
            raise ValueError('setServiceManager requires an IServiceService')



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

Revision information:
$Id: ServiceManagerContainer.py,v 1.1 2002/08/01 18:42:09 jim Exp $
"""

from IServiceManagerContainer import IServiceManagerContainer
from Zope.ComponentArchitecture.IServiceService import IServiceService
from Zope.ComponentArchitecture.Exceptions import ComponentLookupError

_marker = object()

class ServiceManagerContainer:

    __implements__ =  IServiceManagerContainer

    ############################################################
    # Implementation methods for interface
    # Zope.App.ComponentArchitecture.IServiceManagerContainer.

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

    #
    ############################################################


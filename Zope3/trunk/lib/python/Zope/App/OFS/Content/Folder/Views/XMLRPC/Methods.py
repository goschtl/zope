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

$Id: Methods.py,v 1.2 2002/06/10 23:28:01 jim Exp $
"""

from Zope.Publisher.XMLRPC.MethodPublisher import MethodPublisher
from Zope.Publisher.XMLRPC.IXMLRPCPublisher import IXMLRPCPublisher
from Zope.App.PageTemplate import ViewPageTemplateFile


class Methods(MethodPublisher):
    """ """

        
    def __init__(self, folder, request):
        self.context = folder


    def objectIds(self):
        ''' '''
        return self.context.objectIds()


    def setLimit(self, limit):
        ''' '''
        return self.context.setLimit(limit)


    def getLimit(self):
        ''' '''
        return self.context.getLimit()


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

$Id: Methods.py,v 1.3 2002/06/16 18:29:24 srichter Exp $
"""

from Zope.Publisher.XMLRPC.XMLRPCView import XMLRPCView


class Methods(XMLRPCView):
        
    __implements__ = XMLRPCView.__implements__

    def objectIds(self):
        ''' '''
        return self.context.objectIds()


    def setLimit(self, limit):
        ''' '''
        return self.context.setLimit(limit)


    def getLimit(self):
        ''' '''
        return self.context.getLimit()


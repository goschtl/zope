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
$Id: Publication.py,v 1.2 2002/06/10 23:29:20 jim Exp $
"""

from Zope.App.ZopePublication.HTTP.Publication import ZopeHTTPPublication
from Zope.Publisher.Browser.IBrowserPublisher import IBrowserPublisher
from Zope.ComponentArchitecture import queryView
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.Proxy.ProxyIntrospection import removeAllProxies

class BrowserPublication(ZopeHTTPPublication):
    """Web browser publication handling."""
        
    def getDefaultTraversal(self, request, ob):

        r = ()

        if IBrowserPublisher.isImplementedBy(removeAllProxies(ob)):
            r = ob.browserDefault(request)
        else:
            adapter = queryView(ob, '_traverse', request , None)
            if adapter is not None:
                r = adapter.browserDefault(request)
            else:
                return (ob, None)

        if r[0] is ob: return r
        
        wrapped = ContextWrapper(r[0], ob, name=None)
        return (wrapped, r[1])

# For now, have a factory that returns a singleton
class PublicationFactory:

    def __init__(self, db):
        self.__pub = BrowserPublication(db)

    def __call__(self):
        return self.__pub


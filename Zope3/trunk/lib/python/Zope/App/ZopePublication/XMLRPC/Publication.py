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

$Id: Publication.py,v 1.3 2002/06/16 18:40:23 srichter Exp $
"""

from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.App.ZopePublication.HTTP.Publication import ZopeHTTPPublication

class XMLRPCPublication(ZopeHTTPPublication):
    """XML-RPC publication handling.

       There is nothing special here right now.
    """

    def traverseName(self, request, ob, name):

        naked_ob = removeAllProxies(ob)
        if hasattr(ob, name):
            return getattr(ob, name)
        else:
            return super(XMLRPCPublication, self).traverseName(request,
                                                               ob, name)


# For now, have a factory that returns a singleton
class XMLRPCPublicationFactory:

    def __init__(self, db):
        self.__pub = XMLRPCPublication(db)

    def __call__(self):
        return self.__pub

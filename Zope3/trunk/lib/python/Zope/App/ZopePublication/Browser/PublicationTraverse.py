##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: PublicationTraverse.py,v 1.1 2002/06/20 21:47:45 jim Exp $
"""
__metaclass__ = type

from Zope.App.ZopePublication.PublicationTraverse \
     import PublicationTraverser as PublicationTraverser_
from Zope.Publisher.Browser.IBrowserPublisher import IBrowserPublisher
from Zope.ComponentArchitecture import queryAdapter

class PublicationTraverser(PublicationTraverser_):    

    def traverseRelativeURL(self, request, ob, path):

        ob = self.traversePath(request, ob, path)

        while 1:
            adapter = queryAdapter(ob, IBrowserPublisher)
            if adapter is None:
                return ob
            ob, path = adapter.browserDefault(request)
            if not path:
                return ob
                        
            ob = self.traversePath(request, ob, path)

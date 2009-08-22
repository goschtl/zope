##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Resource URL acess

$Id: resources.py 67630 2006-04-27 00:54:03Z jim $
"""
from zope.component import queryAdapter
from zope.interface import implements
from zope.location import locate
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher

class Resources(BrowserView):
    """Provide a URL-accessible resource namespace
    """

    implements(IBrowserPublisher)

    def publishTraverse(self, request, name):
        '''See interface IBrowserPublisher'''

        resource = queryAdapter(request, name=name)
        if resource is None:
            raise NotFound(self, name)

        locate(resource, self.context, name)
        return resource

    def browserDefault(self, request):
        '''See IBrowserPublisher'''
        return empty, ()

    def __getitem__(self, name):
        return self.publishTraverse(self.request, name)


def empty():
    return ''

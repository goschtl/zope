##############################################################################
#
# Copyright (c) 2009 Fabio Tranchitella <fabio@tranchitella.it>
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

"""
$Id$
"""

import bobo

from webob import Request

from z3c.bobopublisher.interfaces import IPublishTraverse, IDefaultViewName, \
    IBrowserPage, IRequest, IGETRequest, IPOSTRequest, IPUTRequest, \
    IDELETERequest

from zope.component import getUtility, queryUtility
from zope.interface import directlyProvides
from zope.location import LocationProxy, locate
from zope.location.interfaces import ILocation, IRoot


class Publication(object):
    """Publication subroute"""

    methods = ('GET', 'HEAD', 'POST', 'PUT', 'DELETE')

    def __init__(self, request, context=None):
        self.request = self._request(request)
        if context is None:
            context = getUtility(IRoot)
        self.context = self.proxy(context)

    def _request(self, request):
        if request.method in (u'GET', u'HEAD'):
            directlyProvides(request, IGETRequest)
        elif request.method == u'POST':
            directlyProvides(request, IPOSTRequest)
        elif request.method == u'PUT':
            directlyProvides(request, IPUTRequest)
        elif request.method == u'DELETE':
            directlyProvides(request, IDELETERequest)
        else:
            directlyProvides(request, IRequest)
        return request

    def proxy(self, object):
        proxy = self.request.environ.get('bobopublisher.proxy')
        if proxy is None:
            return object
        return proxy(object)

    @bobo.resource('')
    def base(self, request):
        return bobo.redirect(request.url + '/')

    @bobo.subroute('/:name')
    def traverse(self, request, name):
        traverser = IPublishTraverse(self.context)
        name = name.decode(request.charset or 'utf-8') or \
            IDefaultViewName(self.context, u'index.html')
        try:
            obj = traverser.publishTraverse(request, name)
        except KeyError:
            raise bobo.NotFound
        if IBrowserPage.providedBy(obj):
            return bobo.query('', method=self.methods)(obj)
        elif hasattr(obj, 'bobo_response'):
            return obj
        elif not ILocation.providedBy(obj):
            obj = LocationProxy(obj)
        locate(obj, self.context, name)
        return Publication(request, obj)

Publication = bobo.subroute('', scan=True)(Publication)

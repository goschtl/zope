##############################################################################
#
# Copyright (c) 2006-2007 Lovely Systems and Contributors.
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
__docformat__ = "reStructuredText"

from interfaces import IResponseCacheSettings
from zope import interface
from zope import component
from zope.schema.fieldproperty import FieldProperty
from lovely.memcached.interfaces import IMemcachedClient
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app.component.hooks import getSite
import re

CKEY_PAT = pat = re.compile(r'\+\+ckey\+\+([^\/]*)\/')

class ResponseCacheSettings(object):

    interface.implements(IResponseCacheSettings)

    cacheName = FieldProperty(IResponseCacheSettings['cacheName'])
    dependencies = FieldProperty(
                    IResponseCacheSettings['dependencies'])
    lifetime= FieldProperty(IResponseCacheSettings['lifetime'])

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._key = None

    @apply
    def key():
        def get(self):
            if self._key is not None:
                return self._key
            url = absoluteURL(self.context, self.request)
            siteUrl = absoluteURL(getSite(), self.request)
            url = url[len(siteUrl):]
            for key in reversed(CKEY_PAT.findall(self.request.getURL())):
                url = '/++ckey++%s%s' % (key, url)
            return url.encode('utf-8')
        def set(self, value):
            self._key = value
        return property(get, set)

    @property
    def cache(self):
        return component.queryUtility(IMemcachedClient,
                                      name=self.cacheName,
                                      context=self.context)


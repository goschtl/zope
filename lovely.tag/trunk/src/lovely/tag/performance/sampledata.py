##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Sampledata for the performance test

$Id$
"""
__docformat__ = 'restructuredtext'

import os
import random

from zope import interface
from zope import component
from zope import schema
from zope import event

from zope.lifecycleevent import ObjectCreatedEvent

from zope.app.component import hooks
from zope.app.container.contained import contained

from z3c.sampledata.interfaces import ISampleDataPlugin

from lovely.tag.interfaces import IUserTagging
from lovely.tag.performance import app


class IUrlsSchema(interface.Interface):
    """Sample generator for urls with tags."""

    numUrls = schema.Int(
            title = u'urls',
            description = u'Number or urls to create.',
            default = 100,
            )


class Urls(object):
    interface.implements(ISampleDataPlugin)

    dependencies = []
    schema = IUrlsSchema

    def generate(self, context, param, dataSource=None, seed=None):
        numUrls = param['numUrls']
        urls = app.UrlContainer()
        event.notify(ObjectCreatedEvent(urls))
        context['urls'] = urls
        dirname = os.path.dirname(__file__)
        self.tags = [unicode(line.strip())
                         for line in file(os.path.join(dirname,
                                          '40000.words')).readlines()]
        self.shorttags = [unicode(line.strip())
                         for line in file(os.path.join(dirname,
                                          '250.words')).readlines()]
        self.domains = [unicode(line.strip())
                         for line in file(os.path.join(dirname,
                                          'domain.txt')).readlines()]
        self.protocol = [unicode(line.strip())
                         for line in file(os.path.join(dirname,
                                          'protocol.txt')).readlines()]
        self.pre = [unicode(line.strip())
                         for line in file(os.path.join(dirname,
                                          'pre.txt')).readlines()]
        self.rand = random.Random()
        self.rand.seed(seed)
        i = 1
        for urlName in self._urls(numUrls):
            url = app.Url()
            event.notify(ObjectCreatedEvent(url))
            url.url = urlName
            urls['%i'%i] = url
            tagging = IUserTagging(url)
            tagging.tags=self._tags(10)
            i+=1
        return urls

    def _tags(self, num, randomLength=True):
        tags = []
        maxRand = len(self.tags)-1
        maxShortRand = len(self.shorttags)-1
        if randomLength:
            num = self.rand.randint(0, num)
        for i in range(num):
            if divmod(i,2)[1]==0:
                tags.append(self.tags[self.rand.randint(0, maxRand)])
            else:
                tags.append(self.shorttags[self.rand.randint(0, maxShortRand)])
        return tags

    def _urls(self, num):
        maxTagsRand = len(self.tags)-1
        for i in range(num):
            protocol = self.protocol[self.rand.randint(0, len(self.protocol)-1)]
            pre      = self.pre[self.rand.randint(0, len(self.pre)-1)]
            firstPart = self.tags[self.rand.randint(0, maxTagsRand)]
            secondPart = self.tags[self.rand.randint(0, maxTagsRand)]
            domain = self.domains[self.rand.randint(0, len(self.domains)-1)]
            thirdPart = self.tags[self.rand.randint(0, maxTagsRand)]
            forthPart = self.tags[self.rand.randint(0, maxTagsRand)]
            yield u'%s%s.%s.%s/%s/%s.html' %(
                        protocol,
                        pre,
                        firstPart,
                        domain,
                        thirdPart,
                        forthPart,
                        )


class IPerformanceTestSiteSamples(interface.Interface):
    """Sample generator for the users bookshelfs."""

    name = schema.TextLine(
            title = u'Name',
            description = u'The name of the site.',
            default = u'Tag Performance'
            )


class PerformanceTestSite(object):
    interface.implements(ISampleDataPlugin)

    dependencies = []
    schema = IPerformanceTestSiteSamples

    def generate(self, context, param, dataSource=None, seed=None):
        name = param['name']
        testsite = app.PerformanceTestSite()
        event.notify(ObjectCreatedEvent(testsite))
        context[name] = testsite
        return testsite

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
"""Tagging Performance Views

$Id$
"""
__docformat__ = "reStructuredText"

import time
import random
import os

from zope import interface
from zope import component
from zope import schema

from zope.formlib import form

from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.intid.interfaces import IIntIds

from lovely.tag.interfaces import ITaggingEngine


class ISearchSchema(interface.Interface):
    """Defines the search fields"""

    tags = schema.TextLine(
            title = u'Tags',
            description = u"""
                The tags to search for.
                If no tags are given :
                    Search for random tags from the file '250.words'.
                    First search with 1 tag, second with 2 tags, third with 3
                    tags and then start again with one tag.
                """,
            required = False,
            )

    repeats = schema.Int(
            title = u'Repeat',
            description = u'Number of times to repeat the search',
            default = 300,
            )

    itemLookup = schema.Bool(
            title = u'Item lookup',
            description = u"""
                Read the items after geting the ids from the tagging engine
                """,
            default = False,
            )


class SearchTags(form.PageForm):

    form_fields = form.Fields(ISearchSchema).select('tags',
                                                    'repeats',
                                                    'itemLookup')

    base_template = form.AddForm.template
    template = ViewPageTemplateFile('searchtags.pt')

    hasTimeValues = False

    @form.action(u'Search')
    def handle_search_action(self, action, data):
        self.rand = random.Random()
        self.rand.seed('tags')
        dirname = os.path.dirname(__file__)
        self.shorttags = [unicode(line.strip())
                         for line in file(os.path.join(dirname,
                                          '250.words')).readlines()]
        start = time.clock()
        self.repeats = data['repeats']
        self.tags = data['tags']
        if self.tags is not None:
            self.tags = data['tags'].split()
        itemLookup = data['itemLookup']
        intids = component.getUtility(IIntIds)
        engine = component.getUtility(ITaggingEngine)
        numTags = 1
        for i in xrange(self.repeats):
            if self.tags is None:
                tags = self.tags
            else:
                if numTags>3:
                    numTags=1
                tags = self._tags(numTags)
                numTags+=1
            itemids = engine.getItems(tags)
            self.numitemsfound = len(itemids)
            self.itemsfound = []
            if itemLookup:
                for itemId in itemids:
                    self.itemsfound.append(intids.getObject(itemId))
        self.totaltime = time.clock() - start
        self.time = self.totaltime / self.repeats
        self.hasTimeValues = True

    def _tags(self, num):
        tags = []
        maxShortRand = len(self.shorttags)-1
        for i in range(num):
            tags.append(self.shorttags[self.rand.randint(0, maxShortRand)])
        return tags


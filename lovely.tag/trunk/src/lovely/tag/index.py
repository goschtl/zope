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
"""A catalog index wich uses the tagging engine.

$Id$
"""
__docformat__ = "reStructuredText"

import persistent
from BTrees.IFBTree import IFTreeSet

from zope import interface
from zope import component

from zope.cachedescriptors.property import Lazy
from zope.index.interfaces import IInjection

from zope.app.container.contained import Contained

from lovely.tag.interfaces import ITaggingEngine, ITagIndex


class TagIndex(persistent.Persistent, Contained):
    interface.implements(ITagIndex, IInjection)

    def __init__(self, engineName=''):
        self.engineName = engineName

    @Lazy
    def engine(self):
        return component.getUtility(ITaggingEngine, name = self.engineName)

    def index_doc(self, docid, value):
        # not used but makes the catalog happy
        pass

    def unindex_doc(self, docid, value):
        # not used but makes the catalog happy
        pass

    def apply(self, query):
        if 'any_of' in query:
            tags = query['any_of']
            items = self.engine.getItems(tags)
        elif 'all_of' in query:
            tags = query['all_of']
            items = None
            for tag in tags:
                it = self.engine.getItems([tag])
                if items is None:
                    items = it
                else:
                    items = items.intersection(it)
                if not items:
                    break
        if items:
            items = [id for id in items]
            return IFTreeSet(items)
        return None


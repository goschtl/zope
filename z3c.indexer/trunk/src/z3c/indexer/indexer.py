##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
from zope.cachedescriptors.property import Lazy
from zope.app.intid.interfaces import IIntIds

from z3c.indexer import interfaces


def index(context):
    """Index object.
    
    This will only call indexes which object have IIndexer adapter for and will
    avoid calling all indexes for each object.
    
    If you use the old indexing pattern, implement a own subscriber which uses
    this pattern for z3c.indexer based indexes.
    """
    adapters = zope.component.getAdapters((context,), interfaces.IIndexer)
    for name, adapter in adapters:
        adapter.doIndex()


def unindex(context):
    """Unindex object.
    
    This will only call indexes which object have IIndexer adapter for and will
    avoid calling all indexes for each object.
    
    If you use the old unindexing pattern, implement a own subscriber which
    uses this pattern for z3c.indexer based indexes.
    """
    adapters = zope.component.getAdapters((context,), interfaces.IIndexer)
    for name, adapter in adapters:
        adapter.doUnIndex()


class IndexerBase(object):
    """Indexer base class.
    
    A IIndexer is registered as a named adapter. This makes it possible to 
    provide more then one adapter per object. You can implement one single 
    IIndexer adapter for your object or more then one. It depends on how you
    like to call them. The global helper method called ``index`` and 
    ``unindex`` above can be used for call all IIndexer in a single call.
    """

    def __init__(self, context):
        """Registered as named index adapter"""
        self.context = context

    @Lazy
    def oid(self):
        """Get IntId for the adapted context."""
        intids = zope.component.getUtility(IIntIds, context=self.context)
        return intids.getId(self.context)

    def doIndex(self):
        """Implement your own indexing pattern."""
        raise NotImplementedError("Subclass must implement doIndex method.")

    def doUnIndex(self):
        """Implement your own un-indexing pattern."""
        raise NotImplementedError("Subclass must implement doUnIndex method.")


# value indexer
class ValueIndexerBase(IndexerBase):
    """Value indexer implementation."""

    indexName = ''

    @Lazy
    def index(self):
        return zope.component.getUtility(interfaces.IIndex, self.indexName,
            context=self.context)

    @property
    def value(self):
        """Get the index value for the adapted context and relevant index."""
        raise NotImplementedError("Subclass must implement value property.")

    def doIndex(self):
        self.index.doIndex(self.oid, self.value)

    def doUnIndex(self):
        self.index.doUnIndex(self.oid)


class ValueIndexer(ValueIndexerBase):
    """Value indexer implementation."""

    zope.interface.implements(interfaces.IValueIndexer)


class ValueAutoIndexer(ValueIndexerBase):
    """Value (auto) indexer implementation."""

    zope.interface.implements(interfaces.IValueAutoIndexer)


# multi indexer
class MultiIndexerBase(IndexerBase):
    """Can be used a s base for index a object in more then one index."""

    def __init__(self, context):
        """Registered as named index adapter"""
        self.context = context

    def getIndex(self, indexName):
        return zope.component.getUtility(interfaces.IIndex, indexName,
            context=self.context)

    def doIndex(self):
        """Implement your own indexing pattern."""
        raise NotImplementedError("Subclass must implement doIndex method.")

    def doUnIndex(self):
        """Implement your own un-indexing pattern."""
        raise NotImplementedError("Subclass must implement doUnIndex method.")


class MultiIndexer(MultiIndexerBase):
    """Can be used a s base for index a object in more then one index."""

    zope.interface.implements(interfaces.IMultiIndexer)


class MultiAutoIndexer(MultiIndexerBase):
    """Can be used a s base for index a object in more then one index."""

    zope.interface.implements(interfaces.IMultiAutoIndexer)

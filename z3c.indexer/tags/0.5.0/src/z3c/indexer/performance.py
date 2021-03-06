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

import time
import persistent
import zope.interface
import zope.component
import zope.schema
import zope.event
import zope.lifecycleevent
import zope.location.interfaces
from ZODB.interfaces import IConnection
from BTrees.IFBTree import difference, IFBTree
from persistent.interfaces import IPersistent
from zope.index.text.textindex import TextIndex as ZTextIndex

from zope.app.keyreference.interfaces import IKeyReference
from zope.app.keyreference.testing import SimpleKeyReference

from zope.app.component import hooks
from zope.app.catalog.interfaces import ICatalog
from zope.app.catalog.text import ITextIndex
from zope.app.catalog.field import FieldIndex as ZFieldIndex
from zope.app.catalog.interfaces import ICatalogIndex
from zope.app.catalog.catalog import Catalog
from zope.app.catalog.catalog import indexAdded
from zope.app.catalog.catalog import indexDocSubscriber
from zope.app.catalog.catalog import reindexDocSubscriber
from zope.app.catalog.catalog import unindexDocSubscriber
from zope.app.container.interfaces import IReadContainer
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.interfaces import IObjectModifiedEvent
from zope.app.container.interfaces import IObjectMovedEvent
from zope.app.container import contained
from zope.app.intid import IntIds
from zope.app.intid import addIntIdSubscriber
from zope.app.intid import removeIntIdSubscriber
from zope.app.intid.interfaces import IIntIds
from zope.app.intid.interfaces import IIntIdAddedEvent
from zope.app.intid.interfaces import IIntIdRemovedEvent
from zope.app.testing import setup

from zc.catalog import index as zcindex

from z3c.indexer import interfaces
from z3c.indexer import subscriber
from z3c.indexer.query import TextQuery
from z3c.indexer.query import Eq
from z3c.indexer.index import TextIndex
from z3c.indexer.index import FieldIndex
from z3c.indexer.index import ValueIndex
from z3c.indexer.indexer import MultiAutoIndexer
from z3c.indexer.search import SearchQuery 


timeResult = None

def timeTest(function, counter=10000, *args, **kw):
    """timer"""
    res = []
    append = res.append
    def wrapper(*args, **kw):
        start_time = time.time()
        for i in range(counter):
            append(function(*args, **kw))
        total_time = time.time() - start_time
        global timeResult
        timeResult = total_time
        return res
    return wrapper(*args, **kw)


def calcSpeedUp(catalogTime, indexerTime):
    try:
        if catalogTime > indexerTime:
            # faster
            precent = int('%.0f' % \
                float(float(catalogTime) / float(indexerTime) * 100 -100))
            return '%4d%s' % (precent, '%')
        else:
            # slower
            precent = int('%.0f' % \
                float(float(indexerTime) / float(catalogTime) * 100 -100))
            return '-%3d%s' % (precent, '%')
    except ZeroDivisionError:
        return '   0'

    


##############################################################################
#
# test components
#
##############################################################################

class IContent(zope.interface.Interface):
    """Sample content."""

    title = zope.schema.TextLine(title=u'Title')
    counter = zope.schema.Int(title=u'Counter')
    time = zope.schema.Datetime(title=u'Time')


class Content(persistent.Persistent, contained.Contained):
    """Sample content."""

    zope.interface.implements(IContent)

    def __init__(self, counter):
        self.title = u'Number %s' % counter
        self.counter = counter
        self.time = time.time()


# catalog index
class CatalogTextIndex(ZTextIndex, contained.Contained):
    """Test index for catalog."""

    def index_doc(self, docid, obj):
        if not IContent.providedBy(obj):
            return
        return super(CatalogTextIndex, self).index_doc(docid, obj.title)


class CatalogValueIndex(zcindex.ValueIndex, contained.Contained):
    """Value Index for catalog setup."""

    def index_doc(self, docid, obj):
        if not IContent.providedBy(obj):
            return
        return super(CatalogValueIndex, self).index_doc(docid, obj.time)


class CatalogFieldIndex(ZFieldIndex, contained.Contained):
    """Value Index for catalog setup."""

    default_field_name = 'counter'
    default_interface = IContent


# indexer
class ContentIndexer(MultiAutoIndexer):
    """Multi indexer for IContent."""

    zope.component.adapts(IContent)

    def __init__(self, context):
        """Registered as named index adapter"""
        super(ContentIndexer, self).__init__(context)
        site = hooks.getSite()
        sm = site.getSiteManager()
        self.textIndex = sm['textIndex']
        self.valueIndex = sm['valueIndex']
        self.fieldIndex = sm['fieldIndex']

    def doIndex(self):
        # index context in textIndex
        self.textIndex.doIndex(self.oid, self.context.title)

        # index context in valueIndex
        self.valueIndex.doIndex(self.oid, self.context.time)

        # index context in fieldIndex
        self.fieldIndex.doIndex(self.oid, self.context.counter)

    def doUnIndex(self):

        # index context in setIndex
        self.textIndex.doUnIndex(self.oid)

        # index context in valueIndex
        self.valueIndex.doUnIndex(self.oid)

        # index context in fieldIndex
        self.fieldIndex.doUnIndex(self.oid)


def setUpIntIds(sm):
    intids = IntIds()
    sm['intids'] = intids
    zope.component.provideUtility(intids, IIntIds)


def setUpAdapter():
    # setup key reference
    zope.component.provideAdapter(SimpleKeyReference, (None,), IKeyReference)

    # provide sub location adapter
    zope.component.provideAdapter(contained.ContainerSublocations,
        (zope.app.container.interfaces.IReadContainer,), 
        zope.location.interfaces.ISublocations)


def setUpSubscribers(gsm):
    gsm.registerHandler(indexAdded, (ICatalogIndex, IObjectAddedEvent))
    gsm.registerHandler(indexDocSubscriber, (IIntIdAddedEvent,))
    gsm.registerHandler(reindexDocSubscriber, (ICatalogIndex, IObjectModifiedEvent))
    gsm.registerHandler(unindexDocSubscriber, (IIntIdRemovedEvent,))
    gsm.registerHandler(addIntIdSubscriber)
    gsm.registerHandler(removeIntIdSubscriber)
    gsm.registerHandler(contained.dispatchToSublocations,
        (zope.location.interfaces.ILocation, IObjectMovedEvent))


def setUpCatalog(amountOfIndexes=0):
    site = setup.placefulSetUp(True)
    setUpAdapter()

    # setup IIntIds
    sm = site.getSiteManager()
    setUpIntIds(sm)

    # setup catalog
    ctlg = Catalog()
    sm['catalog'] = ctlg
    sm.registerUtility(ctlg, ICatalog)
    
    # create and add indexes
    ctlg['textIndex'] = CatalogTextIndex()
    ctlg['valueIndex'] = CatalogValueIndex()
    ctlg['fieldIndex'] =  CatalogFieldIndex()
    # add additional not IContent relevant indexes
    for i in range(amountOfIndexes):
        idxName = 'index-%i' % i
        ctlg[idxName] = CatalogTextIndex()

    # now we are ready and can setup the event subscribers
    gsm = zope.component.getGlobalSiteManager()
    setUpSubscribers(gsm)

    # return site
    return site


def setUpIndexer(amountOfIndexes=0):
    site = setup.placefulSetUp(True)
    setUpAdapter()

    # setup IIntIds
    sm = site.getSiteManager()
    setUpIntIds(sm)
    
    # create and add indexes
    sm['textIndex'] = textIndex  = TextIndex()
    sm['valueIndex'] = valueIndex = ValueIndex()
    sm['fieldIndex'] = fieldIndex = FieldIndex()

    # register indexes as utilities
    sm.registerUtility(textIndex, interfaces.IIndex, name='textIndex')
    sm.registerUtility(valueIndex, interfaces.IIndex, name='valueIndex')
    sm.registerUtility(fieldIndex, interfaces.IIndex, name='fieldIndex')

    # add additional not IContent relevant indexes
    for i in range(amountOfIndexes):
        idxName = 'index-%i' % i
        sm[idxName] = CatalogTextIndex()
        sm.registerUtility(sm[idxName], interfaces.IIndex, name=idxName)

    # provide IAutoIndexer for IContent
    zope.component.provideAdapter(ContentIndexer)

    # now we are ready and can setup the event subscribers
    gsm = zope.component.getGlobalSiteManager()
    setUpSubscribers(gsm)
    zope.component.provideHandler(subscriber.autoIndexSubscriber)
    zope.component.provideHandler(subscriber.autoUnindexSubscriber)

    # return site
    return site

def tearDownCatalog():
    setup.placefulTearDown()

def tearDownIndexer():
    setup.placefulTearDown()


def runCatalogIndexing(site, amountOfObjects=1000):
    # setup component
    for i in range(amountOfObjects):
        content = Content(i)
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(content))
        site[unicode(i)] = content


def runIndexerIndexing(site, amountOfObjects=1000):
    # setup component
    for i in range(amountOfObjects):
        content = Content(i)
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(content))
        site[unicode(i)] = content


def runCatalogUpdate():
    ctlg = zope.component.getUtility(ICatalog)
    ctlg.updateIndexes()


def runIndexerUpdate(site):
    for content in site.values():
        interfaces.IAutoIndexer(content).doIndex()


def runCatalogQuery():
    ctlg = zope.component.getUtility(ICatalog)
    return ctlg.searchResults(textIndex='Number 42', fieldIndex=(41, 43))


def runIndexerQuery():
    textQuery = TextQuery('textIndex', 'Number 42')
    fieldQuery = Eq('fieldIndex', 42)
    searchQuery = SearchQuery(textQuery)
    searchQuery = searchQuery.Or(fieldQuery)
    return searchQuery.apply()


def runCatalogNotQuery():
    ctlg = zope.component.getUtility(ICatalog)
    query = ({'textIndex':'Number', 'fieldIndex':(1, 999999999999999999)})
    found = ctlg.apply(query)

    # get all objects
    intids = zope.component.getUtility(IIntIds)
    
    # and remove the given result
    result = IFBTree()
    for uid in intids:
        result.insert(uid, 0)
    return difference(result, found)


def runIndexerNotQuery():
    textQuery = TextQuery('textIndex', 'Number  42')
    fieldQuery = Eq('fieldIndex', 1)
    searchQuery = SearchQuery(textQuery)
    searchQuery = searchQuery.Not(fieldQuery)
    return searchQuery.apply()


def runObjectModifiedEvent(obj):
    obj.title = u'New'
    zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(obj))


def runParentModifiedEvent(site):
    zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(site))


def runObjectRemove(site):
    # remove one item
    for item in site.values():
        del site[item.__name__]
        return

##############################################################################
#
# performance test
#
# This performance test will show that the default zope.app.catalog based
# indexing pattern is very bad on a large set of indexes. Because the default
# catalog pattern tries to index every object in every index.
#
# The z3c.indexer pattern avoids this because you can implement optimized
# indexing pattern which only index objects in the relevant indexes.
#
##############################################################################

def runTest(repeatTimes, amountOfObjects, amountOfIndexes=0):
    print ""
    print "Run test with"
    print "-------------"
    print "- %i x repeat tests" % repeatTimes
    print "- %i objects" % amountOfObjects
    print "- 3 relevant indexes"
    print "- %i other indexes" % amountOfIndexes
    print "Note, the index update get only processed one time."
    print ""
    print "zope.app.catalog"
    # setup zope.app.catalog based performance test
    catalogSite = setUpCatalog(amountOfIndexes)

    # time catalog indexing
    timeTest(runCatalogIndexing, 1, catalogSite, amountOfObjects)
    runCatalogIndexingTime = timeResult
    print "catalog based indexing time:  %.2f s" % runCatalogIndexingTime

    # time catalog query
    res = timeTest(runCatalogQuery,  repeatTimes)
    runCatalogQueryTime = timeResult
    print "catalog based query time:     %.2f s" % runCatalogQueryTime
    if len(res.pop(0)) != 1:
        print "...bad query result returned"

    # time catalog not query
    res = timeTest(runCatalogNotQuery, repeatTimes)
    runCatalogNotQueryTime = timeResult
    print "catalog based not query time: %.2f s" % runCatalogNotQueryTime
    if len(res.pop(0)) != 1:
        print "...bad query result returned"

    # time catalog indexes update
    timeTest(runCatalogUpdate, 1)
    runCatalogUpdateTime = timeResult
    print "catalog based update time:    %.2f s" % runCatalogUpdateTime

    # time object modified event
    ctlgObj = catalogSite['1']
    timeTest(runObjectModifiedEvent, repeatTimes, ctlgObj)
    runCatalogModifiedTime = timeResult
    print "catalog object modified time: %.2f s" % runCatalogModifiedTime

    # time parent modified event
    timeTest(runParentModifiedEvent, repeatTimes, catalogSite)
    runCatalogParentModifiedTime = timeResult
    print "catalog parent modified time: %.2f s" % runCatalogParentModifiedTime

    # time object remove (IObjectMovedEvent)
    timeTest(runObjectRemove, amountOfObjects, catalogSite)
    runCatalogObjectRemoveTime = timeResult
    print "catalog object remove time:   %.2f s" % runCatalogObjectRemoveTime


    # tear down
    tearDownCatalog()

    # setup z3c.indexer based performance test
    indexerSite = setUpIndexer(amountOfIndexes)

    print ""
    print "z3c.indexer"
    # time indexer indexing
    timeTest(runIndexerIndexing, 1, indexerSite, amountOfObjects)
    runIndexerIndexingTime = timeResult
    print "indexer based indexing time:  %.2f s" % runIndexerIndexingTime

    # time indexer query
    res = timeTest(runIndexerQuery, repeatTimes)
    runIndexerQueryTime = timeResult
    print "indexer based query time:     %.2f s" % runIndexerQueryTime
    if len(res.pop(0)) != 1:
        print "...bad query result returned"

    # time indexer query
    res = timeTest(runIndexerNotQuery, repeatTimes)
    runIndexerNotQueryTime = timeResult
    print "indexer based not query time: %.2f s" % runIndexerNotQueryTime
    if len(res.pop(0)) != 1:
        print "...bad query result returned"

    # time indexer indexes update
    timeTest(runIndexerUpdate, 1, indexerSite)
    runIndexerUpdateTime = timeResult
    print "indexer based update time:    %.2f s" % runIndexerUpdateTime

    # time object modified event
    idObj = indexerSite['1']
    timeTest(runObjectModifiedEvent, repeatTimes, idObj)
    runIndexerModifiedTime = timeResult
    print "indexer object modified time: %.2f s" % runIndexerModifiedTime

    # time parent modified event
    timeTest(runParentModifiedEvent, repeatTimes, indexerSite)
    runIndexerParentModifiedTime = timeResult
    print "indexer parent modified time: %.2f s" % runIndexerParentModifiedTime

    # time object remove (IObjectMovedEvent)
    timeTest(runObjectRemove, amountOfObjects, indexerSite)
    runIndexerObjectRemoveTime = timeResult
    print "indexer object remove time:   %.2f s" % runIndexerObjectRemoveTime

    # tear down
    tearDownIndexer()

    print ""
    print "Result for %i objects with 3 relevant and %i other indexes" % (
        amountOfObjects, amountOfIndexes)
    print " ------------------------------------------------------------------------"
    print "| type    | indexing |   query | not query |  update |  modify |  remove |"
    print " ------------------------------------------------------------------------"
    print "| catalog | % 7.2fs |% 7.2fs |  % 7.2fs |% 7.2fs |% 7.2fs |% 7.2fs |" % (
        runCatalogIndexingTime, runCatalogQueryTime, runCatalogQueryTime,
        runCatalogUpdateTime, runCatalogModifiedTime,
        runCatalogObjectRemoveTime)
    print " ------------------------------------------------------------------------"
    print "| indexer | % 7.2fs |% 7.2fs |  % 7.2fs |% 7.2fs |% 7.2fs |% 7.2fs |" % (
        runIndexerIndexingTime, runIndexerQueryTime, runIndexerNotQueryTime,
        runIndexerUpdateTime, runIndexerModifiedTime,
        runIndexerObjectRemoveTime)
    print " ------------------------------------------------------------------------"
    print "| speedup | % 7.2fs |% 7.2fs |  % 7.2fs |% 7.2fs |% 7.2fs |% 7.2fs |" % (
        (runCatalogIndexingTime - runIndexerIndexingTime), 
        (runCatalogQueryTime - runIndexerQueryTime),
        (runCatalogNotQueryTime - runIndexerNotQueryTime),
        (runCatalogUpdateTime - runIndexerUpdateTime),
        (runCatalogModifiedTime - runIndexerModifiedTime),
        (runCatalogObjectRemoveTime - runIndexerObjectRemoveTime))
    print " ------------------------------------------------------------------------"
    print "| speedup |    %s |   %s |     %s |   %s |   %s |   %s |" %( 
        calcSpeedUp(runCatalogIndexingTime, runIndexerIndexingTime), 
        calcSpeedUp(runCatalogQueryTime, runIndexerQueryTime),
        calcSpeedUp(runCatalogNotQueryTime, runIndexerNotQueryTime),
        calcSpeedUp(runCatalogUpdateTime, runIndexerUpdateTime),
        calcSpeedUp(runCatalogModifiedTime, runIndexerModifiedTime),
        calcSpeedUp(runCatalogObjectRemoveTime, runIndexerObjectRemoveTime))
    print " ------------------------------------------------------------------------"
    print ""


def main():
    runTest(1, 100, 10)
    runTest(1, 100, 50)
    runTest(1000, 100, 10)
    runTest(1000, 100, 50)
    runTest(1000, 10000, 10)
    runTest(1000, 10000, 50)

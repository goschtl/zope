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
import zope.i18nmessageid
from zope.traversing.browser import absoluteURL

from z3c.table import interfaces

_ = zope.i18nmessageid.MessageFactory('z3c')


class BatchProvider(object):
    """Batch provider.

    A batch provider is responsible for rendering the batch HTML and not for
    batching. The batch setup is directly done in the table. A batch provider
    get only used if the table rows is a batch.

    This batch provider offers a batch presentation for a given table. The
    batch provides different configuration options which can be ovreriden in
    custom implementations:
    
    The batch acts like this. If we have more batches then then
    (previousBatchSize + nextBatchSize + 3) then the advanced batch is used.

    If the total amount of items is smaller then the previousBatchSize, current
    item and nextBatchSize. We will render all batch links.
    
    Note, the additional factor 3 is the placeholder for the first, current and
    last item.

    Such a batch look like:

    Renders the link for the first batch, spacers, the amount of links for 
    previous batches, the current batch link, spacers, the amount of links for 
    previous batches and the link for the last batch.
    
    Sample for 1000 items with 100 batches with batchSize of 10 and a     
    previousBatchSize of 3 and a nextBatchSize of 3:
    
    [1] ... [6][7][8][*9*][10][11][12] ... [100]

    """

    zope.interface.implements(interfaces.IBatchProvider)

    batchItems = []

    previousBatchSize = 3
    nextBatchSize = 3
    batchSpacer = u'...'

    def __init__(self, context, request, table):
        self.__parent__ = context
        self.context = context
        self.request = request
        self.table = table
        self.batch = table.rows
        self.batches = table.rows.batches

    def renderBatchLink(self, batch, cssClass=None):
        query = '%s=%s&%s=%s' % (self.table.prefix +'-batchStart', batch.start,
            self.table.prefix +'-batchSize', batch.size)
        tableURL = absoluteURL(self.table, self.request)
        idx = batch.index +1
        css = ' class="%s"' % cssClass
        cssClass = cssClass and css or u''
        return '<a href="%s?%s"%s>%s</a>' % (tableURL, query, cssClass, idx)

    def update(self):
        self.batchItems = []
        total = self.previousBatchSize + self.nextBatchSize + 3
        if total < self.batch.total:

            # setup some batches and indexes
            currentBatchIdx = self.batch.index
            prevIdx = currentBatchIdx - self.previousBatchSize
            nextIdx = currentBatchIdx +1
            firstBatch = self.batches[0]
            lastBatch = self.batches[len(self.batches)-1]

            # add first batch
            self.batchItems.append(firstBatch)

            # there must probably be space
            if firstBatch.index +1 != prevIdx:
                # we skip batches between first batch and first previous batch
                self.batchItems.append(None)

            # add previous batches
            for i in range(self.previousBatchSize):
                # append previous batch
                self.batchItems.append(self.batches[prevIdx])
                prevIdx += 1

            # add current batch
            self.batchItems.append(self.batch)

            # add next batches
            for i in range(self.nextBatchSize):
                # append previous batch
                self.batchItems.append(self.batches[nextIdx])
                nextIdx += 1

            # there must probably be space
            if lastBatch.index -1 != nextIdx:
                # we skip batches between last batch and last next batch
                self.batchItems.append(None)

            # add last batch
            self.batchItems.append(lastBatch)

        else:
            self.batchItems = self.batch.batches

    def render(self):
        self.update()
        res = []
        append = res.append
        idx = 0
        lastIdx = len(self.batchItems)
        for batch in self.batchItems:
            idx += 1
            # render spaces
            if batch is None:
                append(self.batchSpacer)
            elif idx == 1:
                # render first
                append(self.renderBatchLink(batch, 'first'))
            elif batch == self.batch:
                # render current
                append(self.renderBatchLink(batch, 'current'))
            elif idx == lastIdx:
                # render last
                append(self.renderBatchLink(batch, 'last'))
            else:
                append(self.renderBatchLink(batch))
        return u'\n'.join(res)

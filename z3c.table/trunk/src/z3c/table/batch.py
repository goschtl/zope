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


def advanced_subset(batches, currentBatchIdx, prevBatchSize, nextBatchSize):
    """build an advanced subset from a large batch list

    This is used to display batch links for a table.

    arguments:
        batches: all the batches
        currentBatchIdx: index of the current batch
        prevBatchSize: number of displayed batches before the current batch
        nextBatchSize: number of displayed batches after the current batch
    return:
        an advanced reduced list of batches, with None as spaces

    Example:
    We build a large batch, and define a convenient display function::

    >>> from z3c.table.batch import advanced_subset as subset
    >>> batches = range(100) # it works with real batches as well

    We try to get subsets at different levels::

    >>> for i in range(0,6):
    ...    subset(batches, i, 2, 2)
    [0, 1, 2, None, 99]
    [0, 1, 2, 3, None, 99]
    [0, 1, 2, 3, 4, None, 99]
    [0, 1, 2, 3, 4, 5, None, 99]
    [0, None, 2, 3, 4, 5, 6, None, 99]
    [0, None, 3, 4, 5, 6, 7, None, 99]

    >>> for i in range(93, 99):
    ...    subset(batches, i, 2, 2)
    [0, None, 91, 92, 93, 94, 95, None, 99]
    [0, None, 92, 93, 94, 95, 96, None, 99]
    [0, None, 93, 94, 95, 96, 97, None, 99]
    [0, None, 94, 95, 96, 97, 98, 99]
    [0, None, 95, 96, 97, 98, 99]
    [0, None, 96, 97, 98, 99]

    Try with no previous and no next batch::

    >>> subset(batches, 0, 0, 0)
    [0, None, 99]
    >>> subset(batches, 1, 0, 0)
    [0, 1, None, 99]
    >>> subset(batches, 2, 0, 0)
    [0, None, 2, None, 99]

    Try with only 1 previous and 1 next batch:

    >>> subset(batches, 0, 1, 1)
    [0, 1, None, 99]
    >>> subset(batches, 1, 1, 1)
    [0, 1, 2, None, 99]
    >>> subset(batches, 2, 1, 1)
    [0, 1, 2, 3, None, 99]

    Try with incoherent values values::
    >>> subset(batches, 0, -4, -10)
    Traceback (most recent call last):
    ...
    AssertionError
    >>> subset(batches, 2000, 3, 3)
    Traceback (most recent call last):
    ...
    AssertionError
    """
    batchItems = []
    # setup some batches and indexes
    firstIdx = 0
    lastIdx = len(batches) - 1
    assert(currentBatchIdx >= 0 and currentBatchIdx <= lastIdx)
    assert(prevBatchSize >= 0 and nextBatchSize >= 0)
    prevIdx = currentBatchIdx - prevBatchSize
    nextIdx = currentBatchIdx + 1
    firstBatch = batches[0]
    lastBatch = batches[len(batches)-1]

    # add first batch
    if firstIdx < currentBatchIdx:
        batchItems.append(firstBatch)

    # there must probably be space
    if firstIdx + 1 < prevIdx:
        # we skip batches between first batch and first previous batch
        batchItems.append(None)

    # add previous batches
    for i in range(prevIdx, prevIdx+prevBatchSize):
        if firstIdx < i:
            # append previous batches
            batchItems.append(batches[i])

    # add current batch
    batchItems.append(batches[currentBatchIdx])

    # add next batches
    for i in range(nextIdx, nextIdx+nextBatchSize):
        if i < lastIdx:
            # append previous batch
            batchItems.append(batches[i])

    # there must probably be space
    if nextIdx + nextBatchSize < lastIdx:
        # we skip batches between last batch and last next batch
        batchItems.append(None)

    # add last batch
    if currentBatchIdx < lastIdx:
        batchItems.append(lastBatch)
    return batchItems


class BatchProvider(object):
    """Batch provider.

    A batch provider is responsible for rendering the batch HTML and not for
    batching. The batch setup is directly done in the table. A batch provider
    get only used if the table rows is a batch.

    This batch provider offers a batch presentation for a given table. The
    batch provides different configuration options which can be overriden in
    custom implementations:
    
    The batch acts like this. If we have more batches than
    (prevBatchSize + nextBatchSize + 3) then the advanced batch subset is used.
    Otherwise, we will render all batch links.
    
    Note, the additional factor 3 is the placeholder for the first, current and
    last item.

    Such a batch looks like:

    Renders the link for the first batch, spacers, the amount of links for 
    previous batches, the current batch link, spacers, the amount of links for 
    previous batches and the link for the last batch.
    
    Sample for 1000 items with 100 batches with batchSize of 10 and a     
    prevBatchSize of 3 and a nextBatchSize of 3:

    For the first item:
    [*1*][2][3][4] ... [100]

    In the middle:
    [1] ... [6][7][8][*9*][10][11][12] ... [100]

    At the end:
    [1] ... [97][98][99][*100*]
    """

    zope.interface.implements(interfaces.IBatchProvider)

    batchItems = []

    prevBatchSize = 3
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
        # 3 is is the placeholder for the first, current and last item.
        total = self.prevBatchSize + self.nextBatchSize + 3
        if self.batch.total <= total:
            # give all batches
            self.batchItems = self.batch.batches
        else:
            # switch to an advanced batch subset
            self.batchItems = advanced_subset(self.batches,
                                              self.batch.index,
                                              self.prevBatchSize,
                                              self.nextBatchSize,
                                              )

    def render(self):
        self.update()
        res = []
        append = res.append
        idx = 0
        lastIdx = len(self.batchItems)
        for batch in self.batchItems:
            idx += 1
            # build css class
            cssClasses = []
            if batch and batch == self.batch:
                cssClasses.append('current')
            if idx == 1:
                cssClasses.append('first')
            if idx == lastIdx:
                cssClasses.append('last')
            
            if cssClasses:
                css = ' '.join(cssClasses)
            else:
                css = None

            # render spaces
            if batch is None:
                append(self.batchSpacer)
            elif idx == 1:
                # render first
                append(self.renderBatchLink(batch, css))
            elif batch == self.batch:
                # render current
                append(self.renderBatchLink(batch, css))
            elif idx == lastIdx:
                # render last
                append(self.renderBatchLink(batch, css))
            else:
                append(self.renderBatchLink(batch))
        return u'\n'.join(res)

##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Control view for the text index.

XXX longer description goes here.

$Id: control.py,v 1.4 2002/12/30 14:02:53 stevea Exp $
"""

from __future__ import generators

from zope.component import getService, queryAdapter
from zope.exceptions import NotFoundError
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.browser import BrowserView

from zope.app.traversing import locationAsUnicode
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.index.text import IQueryView

class ControlView(BrowserView):

    __implements__ = BrowserView.__implements__, IQueryView

    default_start = 0 # Don't change -- always start at first batch
    default_count = 2 # Default batch size -- tune as you please

    def __init__(self, context, request):
        super(ControlView, self).__init__(context, request)
        self.hub = getService(context, "HubIds")

    def nextBatch(self):
        start = int(self.request.get('start', self.default_start))
        count = int(self.request.get('count', self.default_count))
        return start + count

    def prevBatch(self):
        start = int(self.request.get('start', self.default_start))
        count = int(self.request.get('count', self.default_count))
        return start - count

    def query(self, start=None):
        queryText = self.request.get('queryText', '')
        if start is None:
            start = int(self.request.get('start', self.default_start))
        count = int(self.request.get('count', self.default_count))
        results, total = self.context.query(queryText, start, count)
        nresults = len(results)
        first = start + 1
        last = first + len(results) - 1
        result = {
            'results': list(self._resultIterator(results)),
            'nresults': nresults,
            'first': first,
            'last': last,
            'total': total,
            }
        if start > 0:
            prev = max(0, start - count)
            result['prev'] = prev
        if last < total:
            next = start + count
            result['next'] = next
        return result

    def _resultIterator(self, results):
        for hubid, score in results:
            yield self._cookInfo(hubid, score)

    def _cookInfo(self, hubid, score):
        location = locationAsUnicode(self.hub.getLocation(hubid))
        scoreLabel = "%.1f%%" % (100.0 * score)
        result = {
            'location': location,
            'score': score,
            'scoreLabel': scoreLabel,
            }
        try:
            object = self.hub.getObject(hubid)
        except NotFoundError:
            pass
        else:
            dc = queryAdapter(object, IZopeDublinCore, context=self.context)
            if dc is not None:
                title = dc.title
                result['title'] = title
        return result

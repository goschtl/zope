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

$Id: control.py,v 1.2 2003/06/23 16:44:38 mgedmin Exp $
"""

from __future__ import generators

from zope.interface import implements
from zope.component import getService, queryAdapter
from zope.app.services.servicenames import HubIds
from zope.exceptions import NotFoundError
from zope.publisher.browser import BrowserView

from zope.app.traversing import canonicalPath
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.index.text import IQueryView
from zope.app.browser.component.interfacewidget import interfaceToName

class ControlView(BrowserView):

    implements(IQueryView)

    def __init__(self, context, request):
        super(ControlView, self).__init__(context, request)
        self.hub = getService(context, HubIds)

    def interface_name(self):
        return interfaceToName(self.context.interface)

    def query(self):
        queryText = self.request.get('queryText', '')
        results = self.context.search(queryText)
        nresults = len(results)
        first = 1
        last = first + len(results) - 1
        result = {
            'results': list(self._resultIterator(results)),
            'nresults': nresults,
            'first': first,
            'last': last,
            'total': nresults,
            }
        return result

    def _resultIterator(self, results):
        for hubid in results:
            yield self._cookInfo(hubid)

    def _cookInfo(self, hubid):
        location = canonicalPath(self.hub.getPath(hubid))
        # XXX `location` is later used as a URL in a page template, using a
        #     physical path instead of absolute_url will break virtual hosting.
        result = {
            'location': location,
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

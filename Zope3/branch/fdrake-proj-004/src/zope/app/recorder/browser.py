##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
Browser views for the HTTP session recorder.

$Id$
"""
__docformat__ = 'restructuredtext'

import re
import sys
import urllib
import datetime
from cStringIO import StringIO
from zope.interface import Interface
from zope.schema import Text
from zope.app.form.utility import setUpWidgets, getWidgetsData
from zope.app.form.interfaces import IInputWidget, WidgetsError
from zope.app.publisher.browser import BrowserView
from zope.app import recorder
from zope.app.testing import dochttp
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.publisher.interfaces import NotFound


class IRecorderSessionsFilterForm(Interface):
    """Form for filtering recorded requests."""

    skip_urls = Text(title=_(u"URLs to ignore"),
                     description=_(u"""A list of regular expressions.

                     Requests whose paths match any of the expressions listed
                     here will not be shown."""),
                     required=False,
                     default=u'')


class RecordedSessionsView(BrowserView):
    """View for /++etc++process/RecordedSessions.html"""

    error = None

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        setUpWidgets(self, IRecorderSessionsFilterForm, IInputWidget)

    def _skip_urls(self):
        """Extract URL regexes from the request.

        Returns a multi-line string.
        """
        try:
            data = getWidgetsData(self, IRecorderSessionsFilterForm)
        except WidgetsError:
            return ''
        return data.get('skip_urls') or ''

    def _skip_urls_as_regexes(self):
        """Extract URL regexes from the request.

        Returns an iterator of compiled regex objects.

        Skips invalid regexes and sets self.error.
        """
        for pattern in self._skip_urls().splitlines():
            if pattern.strip():
                try:
                    yield re.compile(pattern)
                except re.error:
                    self.error = _('Invalid regex: %s') % pattern

    def _requests(self):
        """List all requests that should be shown on the page.

        Performs filtering by URL regexps.

        Returns an iterator of dicts packed with information.
        """
        skip_urls = list(self._skip_urls_as_regexes())
        formatter = self.request.locale.dates.getFormatter('dateTime', 'short')
        requests = [(rq.timestamp, rq) for rq in recorder.requestStorage]
        requests.sort()
        for timestamp, rq in requests:
            for skip_url in skip_urls:
                if skip_url.search(rq.path):
                    break
            else:
                info = {}
                info['object'] = rq
                dt = datetime.datetime.fromtimestamp(rq.timestamp)
                info['time'] = formatter.format(dt)
                info['method'] = rq.method
                info['path'] = rq.path
                info['request_length'] = len(rq.request_string)
                info['response_length'] = len(rq.response_string)
                info['status'] = rq.status
                info['id'] = rq.id
                yield info

    requests = property(lambda self: list(self._requests()))

    def recordedRequest(self, id):
        """Return a request string as text/plain."""
        rq = recorder.requestStorage.get(id)
        if rq is None:
            raise NotFound(self.context, id)
        self.request.response.setHeader('Content-Type', 'text/plain')
        return rq.request_string

    def recordedResponse(self, id):
        """Return a response string as text/plain."""
        rq = recorder.requestStorage.get(id)
        if rq is None:
            raise NotFound(self.context, id)
        self.request.response.setHeader('Content-Type', 'text/plain')
        return rq.response_string

    def __call__(self):
        """Render the page and process forms."""
        if 'CLEAR' in self.request:
            return self.clear()
        if 'FTEST' in self.request:
            return self.makeFTest()
        return self.index()

    def clear(self):
        """Clear all stored requests."""
        recorder.requestStorage.clear()
        url = str(self.request.URL)
        skip_urls = self._skip_urls()
        if skip_urls:
            url += '?field.skip_urls=' + urllib.quote(skip_urls)
        self.request.response.redirect(url)
        return ''

    def makeFTest(self):
        """Create a functional doctest from selected requests."""
        requests = map(recorder.requestStorage.get, self.request.get('id', []))
        requests = filter(None, requests)
        self.request.response.setHeader('Content-Type', 'text/plain')
        self.request.response.setHeader('Content-Disposition',
                                        'attachment; filename="ftest.txt"')
        return make_doctest(requests)


def make_doctest(requests):
    """Convert a list of RecordedRequest objects into a doctest."""
    options, args = dochttp.parser.parse_args(dochttp.default_options)
    skip_rq_headers = [name.lower()
                       for name in (options.skip_request_header or ())]
    skip_rs_headers = [name.lower()
                       for name in (options.skip_response_header or ())]
    old_stdout = sys.stdout
    try:
        sys.stdout = StringIO()
        for rq in requests:
            request = dochttp.Message(StringIO(rq.request_string),
                                      skip_rq_headers)
            response = dochttp.Message(StringIO(rq.response_string),
                                       skip_rs_headers)
            dochttp.output_test(request, response, options.clean_redirects)
        return sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout


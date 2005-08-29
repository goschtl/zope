#!/usr/bin/env python2.3
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
Unit tests for zope.app.recorder.

$Id$
"""
__docformat__ = 'restructuredtext'

import unittest
import transaction
from zope.testing import doctest
from zope.publisher.browser import TestRequest
from zope.app.testing import setup, ztapi
from zope.app.publisher.browser import BrowserView


def doctest_RecordingHTTPServer():
    r"""Unit tests for RecordingHTTPServer.

    We will use stubs instead of real channel and request parser objects, to
    keep the test fixture small.

        >>> from zope.app.recorder import RecordingHTTPTask
        >>> channel = ChannelStub()
        >>> request_data = RequestDataStub()
        >>> task = RecordingHTTPTask(channel, request_data)

    RecordingHTTPTask is a thin wrapper around HTTPTask.  It records all data
    written through task.write, plus the response header, of course.

        >>> task.write('request body\n')
        >>> task.write('goes in here')

    We need to strip CR characters, as they confuse doctest.

        >>> print task.getRawResponse().replace('\r', '')
        HTTP/1.1 200 Ok
        Connection: close
        Server: Stub Server
        <BLANKLINE>
        request body
        goes in here

    """


def doctest_RecordingHTTPRequestParser():
    r"""Unit tests for RecordingHTTPRequestParser.

        >>> from zope.app.recorder import RecordingHTTPRequestParser
        >>> from zope.server.adjustments import default_adj
        >>> parser = RecordingHTTPRequestParser(default_adj)

    RecordingHTTPRequestParser is a thin wrapper around HTTPRequestParser.  It
    records all data consumed by parser.received.

        >>> parser.received('GET / HTTP/1.1\r\n')
        16
        >>> parser.received('Content-Length: 3\r\n')
        19
        >>> parser.received('\r\n')
        2
        >>> parser.received('abc plus some junk')
        3

    We need to strip CR characters, as they confuse doctest.

        >>> print parser.getRawRequest().replace('\r', '')
        GET / HTTP/1.1
        Content-Length: 3
        <BLANKLINE>
        abc

    """


def doctest_RecordingHTTPServer():
    r"""Unit tests for RecordingHTTPServer.

    RecordingHTTPServer is a very thin wrapper over PublisherHTTPServer. First
    we create a custom request:

        >>> class RecorderRequest(TestRequest):
        ...     publication = PublicationStub()

    Further, to keep things simple, we will override the constructor and
    prevent it from listening on sockets.

        >>> from zope.app.recorder import RecordingHTTPServer
        >>> class RecordingHTTPServerForTests(RecordingHTTPServer):
        ...     def __init__(self):
        ...         self.request_factory = RecorderRequest
        >>> server = RecordingHTTPServerForTests()

    We will need a request parser

        >>> from zope.app.recorder import RecordingHTTPRequestParser
        >>> from zope.server.adjustments import default_adj
        >>> parser = RecordingHTTPRequestParser(default_adj)
        >>> parser.received('GET / HTTP/1.1\r\n\r\n')
        18

    We will also need a task

        >>> from zope.app.recorder import RecordingHTTPTask
        >>> channel = ChannelStub()
        >>> task = RecordingHTTPTask(channel, parser)
        >>> task.start_time = 42

    Go!

        >>> server.executeRequest(task)

    Let's see what we got:

        >>> from zope.app import recorder
        >>> len(recorder.requestStorage)
        1
        >>> rq = iter(recorder.requestStorage).next()
        >>> rq.timestamp
        42
        >>> rq.request_string
        'GET / HTTP/1.1\r\n\r\n'
        >>> rq.method
        'GET'
        >>> rq.path
        '/'
        >>> print rq.response_string.replace('\r', '')
        HTTP/1.1 599 No status set
        Content-Length: 0
        X-Powered-By: Zope (www.zope.org), Python (www.python.org)
        Server: Stub Server
        <BLANKLINE>
        <BLANKLINE>
        >>> rq.status
        599
        >>> rq.reason
        'No status set'

    Clean up:

        >>> recorder.requestStorage.clear()

    """


def doctest_RequestStorage():
    r"""Unit tests for RequestStorage.

    RequestStorage uses MappingStorage for transactional data storage, shared
    between threads.  Initially the storage is empty

        >>> from zope.app.recorder import RequestStorage
        >>> storage = RequestStorage()
        >>> len(storage)
        0
        >>> list(storage)
        []

    Request IDs are allocated sequentially

        >>> from zope.app.recorder import RecordedRequest
        >>> storage.add(RecordedRequest(42, 'request', 'response'))
        >>> storage.add(RecordedRequest(43, 'request', 'response'))
        >>> len(storage)
        2
        >>> [(r.id, r.timestamp) for r in storage]
        [(1, 42), (2, 43)]

        >>> storage.get(1).timestamp
        42
        >>> storage.get(2).timestamp
        43
        >>> storage.get(3) is None
        True

    You can clear the storage

        >>> storage.clear()
        >>> len(storage)
        0
        >>> list(storage)
        []

    """


def doctest_make_doctest():
    r'''Unit tests for make_doctest.

        >>> from zope.app.recorder.browser import make_doctest
        >>> from zope.app.recorder import RecordedRequest
        >>> rq1 = RecordedRequest(0, 'GET / HTTP/1.1\r\n\r\n',
        ...                       'HTTP/1.1 200 OK\r\n'
        ...                       'Content-Length: 13\r\n\r\n'
        ...                       'Hello, world!')
        >>> rq2 = RecordedRequest(0, 'GET /bye.html HTTP/1.1\r\n\r\n',
        ...                       'HTTP/1.1 200 OK\r\n'
        ...                       'Content-Length: 15\r\n\r\n'
        ...                       'Goodbye, world!')
        >>> s = make_doctest([rq1, rq2])
        >>> print '|' + s.replace('\n', '\n|')
        |
        |
        |  >>> print http(r"""
        |  ... GET / HTTP/1.1
        |  ... """)
        |  HTTP/1.1 200 OK
        |  Content-Length: 13
        |  <BLANKLINE>
        |  Hello, world!
        |
        |
        |  >>> print http(r"""
        |  ... GET /bye.html HTTP/1.1
        |  ... """)
        |  HTTP/1.1 200 OK
        |  Content-Length: 15
        |  <BLANKLINE>
        |  Goodbye, world!
        |

    '''


def doctest_RecordedSessionsView_skip_urls():
    """Unit test for RecordedSessionsView._skip_urls

        >>> setUpBrowser()

        >>> from zope.app.recorder.browser import RecordedSessionsView
        >>> context = None
        >>> request = TestRequest()
        >>> view = RecordedSessionsView(context, request)

    No skip_urls in the request.

        >>> view._skip_urls()
        ''

    Empty skip_urls field

        >>> request.form['field.skip_urls'] = u''
        >>> view._skip_urls()
        ''

    Non-empty skip_urls

        >>> request.form['field.skip_urls'] = u'/@@/'
        >>> view._skip_urls()
        u'/@@/'

        >>> tearDownBrowser()

    """


def doctest_RecordedSessionsView_skip_urls_as_regexes():
    r"""Unit test for RecordedSessionsView._skip_urls_as_regexes

        >>> setUpBrowser()

        >>> from zope.app.recorder.browser import RecordedSessionsView
        >>> context = None
        >>> request = TestRequest()
        >>> view = RecordedSessionsView(context, request)

    No skip_urls in the request.

        >>> list(view._skip_urls_as_regexes())
        []

    Valid regexes (note that empty lines are skipped)

        >>> request.form['field.skip_urls'] = u'/@@/\n \nxyzzy'
        >>> list(view._skip_urls_as_regexes()) # doctest: +ELLIPSIS
        [<_sre.SRE_Pattern object...>, <_sre.SRE_Pattern object...>]
        >>> r1, r2 = view._skip_urls_as_regexes()
        >>> r1.search('/@@/icon.png') # doctest: +ELLIPSIS
        <...Match object...>
        >>> r2.search('/foo/xyzzy.html') # doctest: +ELLIPSIS
        <...Match object...>

    An invalid regexp

        >>> request.form['field.skip_urls'] = u'/@@/\n++etc++\n'
        >>> list(view._skip_urls_as_regexes()) # doctest: +ELLIPSIS
        [<_sre.SRE_Pattern object...>]
        >>> r1, = view._skip_urls_as_regexes()
        >>> r1.search('/@@/icon.png') # doctest: +ELLIPSIS
        <...Match object...>
        >>> view.error
        u'Invalid regex: ++etc++'

        >>> tearDownBrowser()

    """


def doctest_RecordedSessionsView_requests():
    r"""Unit test for RecordedSessionsView._requests

        >>> setUpBrowser()

        >>> from zope.app.recorder.browser import RecordedSessionsView
        >>> context = None
        >>> request = TestRequest()
        >>> view = RecordedSessionsView(context, request)

    No recorded requests

        >>> view.requests
        []

    Let's add a couple

        >>> from zope.app import recorder
        >>> recorder.requestStorage.add(recorder.RecordedRequest(timestamp=0,
        ...         request_string='GET /something HTTP/1.1\r\n\r\n',
        ...         response_string='HTTP/1.1 404 Not Found\r\n\r\n',
        ...         method='GET', path='/something', status=404,
        ...         ))
        >>> recorder.requestStorage.add(recorder.RecordedRequest(timestamp=1,
        ...         request_string='GET /something_else HTTP/1.1\r\n\r\n',
        ...         response_string='HTTP/1.1 200 OK\r\n\r\n',
        ...         method='GET', path='/something_else', status=200,
        ...         ))

    (Note that although the timestamps are constant (0 is 1st Jan 1970,
    midnight UTC), the returned value depends on the time zone of the system on
    which you run the tests.  I hope that at least the time format is
    constant.)

        >>> from zope.testing.doctestunit import pprint
        >>> pprint(view.requests)       # doctest: +ELLIPSIS
        [{'id': 1,
          'method': 'GET',
          'object': <zope.app.recorder.RecordedRequest object at ...>,
          'path': '/something',
          'request_length': 27,
          'response_length': 26,
          'status': 404,
          'time': u'.../.../... ...:...'},
         {'id': 2,
          'method': 'GET',
          'object': <zope.app.recorder.RecordedRequest object at ...>,
          'path': '/something_else',
          'request_length': 32,
          'response_length': 19,
          'status': 200,
          'time': u'.../.../... ...:...'}]

        >>> tearDownBrowser()
        >>> recorder.requestStorage.clear()

    """


def doctest_RecordedSessionsView_recordedRequest():
    r"""Unit test for RecordedSessionsView.recordedRequest

        >>> setUpBrowser()

        >>> from zope.app.recorder.browser import RecordedSessionsView
        >>> context = None
        >>> request = TestRequest()
        >>> view = RecordedSessionsView(context, request)

        >>> from zope.app import recorder
        >>> recorder.requestStorage.add(recorder.RecordedRequest(timestamp=0,
        ...         request_string='GET /something HTTP/1.1\r\n\r\n',
        ...         response_string='HTTP/1.1 404 Not Found\r\n\r\n',
        ...         method='GET', path='/something', status=404,
        ...         ))

        >>> view.recordedRequest(1)
        'GET /something HTTP/1.1\r\n\r\n'
        >>> request.response.getHeader('Content-Type')
        'text/plain'

        >>> view.recordedRequest(42)
        Traceback (most recent call last):
          ...
        NotFound: Object: None, name: 42

        >>> recorder.requestStorage.clear()
        >>> tearDownBrowser()

    """


def doctest_RecordedSessionsView_recordedResponse():
    r"""Unit test for RecordedSessionsView.recordedResponse

        >>> setUpBrowser()

        >>> from zope.app.recorder.browser import RecordedSessionsView
        >>> context = None
        >>> request = TestRequest()
        >>> view = RecordedSessionsView(context, request)

        >>> from zope.app import recorder
        >>> recorder.requestStorage.add(recorder.RecordedRequest(timestamp=0,
        ...         request_string='GET /something HTTP/1.1\r\n\r\n',
        ...         response_string='HTTP/1.1 404 Not Found\r\n\r\n',
        ...         method='GET', path='/something', status=404,
        ...         ))

        >>> view.recordedResponse(1)
        'HTTP/1.1 404 Not Found\r\n\r\n'
        >>> request.response.getHeader('Content-Type')
        'text/plain'

        >>> view.recordedResponse(42)
        Traceback (most recent call last):
          ...
        NotFound: Object: None, name: 42

        >>> recorder.requestStorage.clear()
        >>> tearDownBrowser()

    """


def doctest_RecordedSessionsView_clear():
    r"""Unit test for RecordedSessionsView.clear

        >>> setUpBrowser()

        >>> from zope.app.recorder.browser import RecordedSessionsView
        >>> context = None
        >>> request = TestRequest()
        >>> view = RecordedSessionsView(context, request)

        >>> from zope.app import recorder
        >>> recorder.requestStorage.add(recorder.RecordedRequest(timestamp=0,
        ...         request_string='GET /something HTTP/1.1\r\n\r\n',
        ...         response_string='HTTP/1.1 404 Not Found\r\n\r\n',
        ...         method='GET', path='/something', status=404,
        ...         ))

    The 'clear' method clears all stored requests and redirects back to the
    page.

        >>> view.clear()
        ''

        >>> list(recorder.requestStorage)
        []

        >>> request.response.getStatus()
        302
        >>> request.response.getHeader('Location')
        'http://127.0.0.1'

    The value of skip_urls is not lost.

        >>> request.form['field.skip_urls'] = u'/@@/\n+'
        >>> view.clear()
        ''
        >>> request.response.getHeader('Location')
        'http://127.0.0.1?field.skip_urls=/%40%40/%0A%2B'

        >>> recorder.requestStorage.clear()
        >>> tearDownBrowser()

    """


def doctest_RecordedSessionsView_makeFTest():
    r"""Unit test for RecordedSessionsView.makeFTest

        >>> setUpBrowser()

        >>> from zope.app.recorder.browser import RecordedSessionsView
        >>> context = None
        >>> request = TestRequest()
        >>> view = RecordedSessionsView(context, request)

        >>> from zope.app import recorder
        >>> recorder.requestStorage.add(recorder.RecordedRequest(timestamp=0,
        ...         request_string='GET /something HTTP/1.1\r\n\r\n',
        ...         response_string='HTTP/1.1 404 Not Found\r\n\r\n',
        ...         method='GET', path='/something', status=404,
        ...         ))

    The 'makeFTest' method creates a doctest and returns it.  You need to
    specify a list of request IDs.  IDs of nonexistent requests are silently
    ignored.

        >>> request.form['id'] = [1, 42]

        >>> print view.makeFTest() # doctest: +ELLIPSIS
        <BLANKLINE>
        ...>>> print http(...
        ...404 Not Found...

        >>> request.response.getHeader('Content-Type')
        'text/plain'
        >>> request.response.getHeader('Content-Disposition')
        'attachment; filename="ftest.txt"'

        >>> recorder.requestStorage.clear()
        >>> tearDownBrowser()

    """


def doctest_RecordedSessionsView_call():
    r"""Unit test for RecordedSessionsView.__call__

        >>> setUpBrowser()

        >>> from zope.app.recorder.browser import RecordedSessionsView
        >>> context = None
        >>> request = TestRequest()
        >>> request.setPrincipal(PrincipalStub)
        >>> view = RecordedSessionsView(context, request)

    view.index is a page template that appears thanks to ZCML magic.

        >>> from zope.app.pagetemplate.viewpagetemplatefile \
        ...     import ViewPageTemplateFile, BoundPageTemplate
        >>> view.index = BoundPageTemplate(ViewPageTemplateFile('sessions.pt'),
        ...                                view)

        >>> from zope.app import recorder
        >>> recorder.requestStorage.add(recorder.RecordedRequest(timestamp=0,
        ...         request_string='GET /something HTTP/1.1\r\n\r\n',
        ...         response_string='HTTP/1.1 404 Not Found\r\n\r\n',
        ...         method='GET', path='/something', status=404,
        ...         ))

        >>> 

    Simple rendering:

        >>> print view() # doctest: +ELLIPSIS,+NORMALIZE_WHITESPACE
        <html>
        ...
          <form method="POST" action="http://127.0.0.1">
            <input class="hiddenType" id="field.skip_urls" name="field.skip_urls" type="hidden" value=""  />
            <table>
              <tr>
                <th>&nbsp;</th>
                <th>Time</th>
                <th>Method</th>
                <th>Path</th>
                <th>Status</th>
              </tr>
              <tr>
                <td><input type="checkbox" name="id:int:list"
                           checked="checked" id="chk1" value="1" /></td>
                <td><label for="chk1">...</label></td>
                <td><a href="RecordedRequest.html?id:int=1">GET</a></td>
                <td><label for="chk1">/something</label></td>
                <td><a href="RecordedResponse.html?id:int=1">404</a></td>
              </tr>
            </table>
        <BLANKLINE>
            <div class="row">
              <div class="control">
                <input type="submit" name="FTEST"
                       value="Create Functional Doctest" />
                <input type="submit" name="CLEAR" value="Clear All" />
              </div>
            </div>
          </form>
        ...

    'FTEST' button:

        >>> request.form['FTEST'] = u"Create Functional Doctest"
        >>> request.form['id'] = [1]
        >>> print view() # doctest: +ELLIPSIS,+NORMALIZE_WHITESPACE
        <BLANKLINE>
        ...>>> print http(...

    'CLEAR' button:

        >>> del request.form['FTEST']
        >>> request.form['CLEAR'] = u"Clear All"
        >>> print view()
        <BLANKLINE>
        >>> request.response.getStatus()
        302
        >>> request.response.getHeader('Location')
        'http://127.0.0.1'

        >>> recorder.requestStorage.clear()
        >>> tearDownBrowser()

    """



class ServerStub(object):
    """Stub for HTTPServer."""

    SERVER_IDENT = 'Stub Server'
    server_name = 'RecordingHTTPServer'
    port = 8081


class ChannelStub(object):
    """Stub for HTTPServerChannel."""

    server = ServerStub()
    creation_time = 42
    addr = ('addr', )

    def write(self, data):
        pass


class RequestDataStub(object):
    """Stub for HTTPRequestParser."""

    version = "1.1"
    headers = {}


class PublicationStub(object):
    """Stub for Publication."""

    def handleException(self, *args):
        pass

    def endRequest(self, request, object):
        pass


class PrincipalStub(object):
    """Stub for request.principal."""

    title = 'Random user'


class ViewGetMenuStub(BrowserView):
    """Stub for @@view_get_menu"""

    def __getitem__(self, name):
        return []


def setUpBrowser(test=None):
    """Set up for zope.app.recorder.browser doctests"""
    setup.placelessSetUp()
    setup.setUpTraversal()

    # Widgets need some setup
    from zope.schema.interfaces import IText
    from zope.app.form.browser.textwidgets import TextAreaWidget
    from zope.app.form.interfaces import IInputWidget
    ztapi.browserViewProviding(IText, TextAreaWidget, IInputWidget)

    # ++view++ namespace
    from zope.app.traversing.interfaces import ITraversable
    import zope.app.traversing.namespace
    ztapi.provideView(None, None, ITraversable, 'view',
                      zope.app.traversing.namespace.view)

    # Macros
    from zope.app.basicskin.standardmacros import StandardMacros
    from zope.app.form.browser.macros import FormMacros
    from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
    ztapi.browserView(None, 'standard_macros', StandardMacros)
    ztapi.browserView(None, 'view_macros',
                      SimpleViewClass("../basicskin/view_macros.pt"))
    ztapi.browserView(None, 'form_macros', FormMacros)
    ztapi.browserView(None, 'widget_macros',
                      SimpleViewClass('../form/browser/widget_macros.pt'))
    ztapi.browserView(None, 'view_get_menu', ViewGetMenuStub)


def tearDownBrowser(test=None):
    """Tear down for zope.app.recorder.browser doctests"""
    setup.placelessTearDown()


def tearDown(test=None):
    """Tear down for zope.app.recorder doctests."""
    transaction.abort()


def test_suite():
    return unittest.TestSuite([doctest.DocTestSuite(tearDown=tearDown)])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

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

import time
import unittest
import transaction
from zope.testing import doctest
from zope.publisher.browser import TestRequest
from zope.app.testing import setup, ztapi
from zope.app.publisher.browser import BrowserView


def doctest_RecordingProtocol():
    r"""Unit tests for ``RecordingProtocol``.

    To create a recording protocol we need a protocol and a factory. To keep
    the test fixture small, we are using a stub implementation for the
    protocol

      >>> protocol = ProtocolStub()

    and the factory is created with a provided function:

      >>> from zope.app import recorder
      >>> db = 'ZODB'
      >>> factory = recorder.createRecordingHTTPFactory(db)

    We can now instantiate the recording protcol:

      >>> recording = recorder.RecordingProtocol(factory, protocol)
      >>> recording.transport = TransportStub()
      >>> factory.protocols = {recording: 1}

    When we now send data to the protocol,

      >>> recording.dataReceived('GET / HTTP/1.1\n\n')
      >>> recording.dataReceived('hello world!\n')

    then the result is immediately available in the ``input`` attribute:

      >>> print recording.input.getvalue()
      GET / HTTP/1.1
      <BLANKLINE>
      hello world!
      <BLANKLINE>

    Once the request has been processed, the response is written

      >>> recording.writeSequence(('HTTP/1.1 200 Okay.\n',
      ...                          'header1: value1\n',
      ...                          'header2: value2\n'))
      >>> recording.write('\n')
      >>> recording.write('This is my answer.')

    and we can again look at it:

      >>> print recording.output.getvalue()
      HTTP/1.1 200 Okay.
      header1: value1
      header2: value2
      <BLANKLINE>
      This is my answer.

    Once the request is finished and the response is written, the connection
    is closed and a recorded request obejct is written:

      >>> recording.connectionLost(None)

    Let's now inspect the recorded requets object:

      >>> len(recorder.requestStorage)
      1
      >>> rq = iter(recorder.requestStorage).next()
      >>> rq.timestamp < time.time()
      True
      >>> rq.request_string
      'GET / HTTP/1.1\n\nhello world!\n'
      >>> rq.method
      'GET'
      >>> rq.path
      '/'
      >>> print rq.response_string.replace('\r', '')
      HTTP/1.1 200 Okay.
      header1: value1
      header2: value2
      <BLANKLINE>
      This is my answer.

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


class ChannelRequestStub(object):

    command = 'GeT'
    path = '/'


class TransportStub(object):
    
    def write(self, data):
        pass
    
    def writeSequence(self, data):
        pass


class ProtocolStub(object):
    """Stub for the HTTP Protocol"""

    requests = [ChannelRequestStub()]

    def dataReceived(self, data):
        pass

    def connectionLost(self, reason):
        pass


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

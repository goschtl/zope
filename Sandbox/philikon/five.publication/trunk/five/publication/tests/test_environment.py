import unittest
import zope.component
from StringIO import StringIO
from zope.testing.cleanup import CleanUp
from zope.publisher.http import HTTPCharsets
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from five.publication.request import BrowserRequest

test_environ = {
    # XXX better cookie
    'HTTP_COOKIE': 'tree-s=eJzT0MgpMOQKVneEA1dbda4CI67EkgJjLj0AeGcHew',
    'SCRIPT_NAME': '',
    'REQUEST_METHOD': 'GET',
    'PATH_INFO': '/john/mc/clane',
    'SERVER_PROTOCOL': 'HTTP/1.1',
    'QUERY_STRING': 'gun=reload&terrorist=kill',
    'CONTENT_LENGTH': '0',
    'SERVER_NAME': 'diehard.tv',
    'REMOTE_ADDR': '127.0.0.1',
    'SERVER_PORT': '8080',
    'CONTENT_TYPE': 'application/x-www-form-urlencoded',
    'QUERY_STRING': 'gun=reload&terrorist=kill',
    'HTTP_ACCEPT_CHARSET': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'HTTP_CONNECTION': 'keep-alive',
    'HTTP_HOST': 'diehard.tv:8080',
    'HTTP_ACCEPT': 'application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,*/*;q=0.5',
    'HTTP_ACCEPT_LANGUAGE': 'en-us,en;q=0.5',
    'HTTP_ACCEPT_ENCODING': 'gzip,deflate',
    'HTTP_KEEP_ALIVE': '300'
    }

class TestEnvironment(unittest.TestCase):
    """
    Test various aspects of the request's behaviour regarding the
    CGI/WSGI environment and other environment variables.
    """

    def test_url(self):
        # ZPublisher's HTTPRequest allows to access different sub-URLs
        # of the current URL as URL0, URL1, URL2, etc.  This is the
        # equivalent of calling request.getURL(n) for zope.publisher's
        # request.
        request = self.makeRequest()
        self.assertEqual(request['URL'], 'http://diehard.tv:8080/john/mc/clane')
        self.assertEqual(request['URL0'], 'http://diehard.tv:8080/john/mc/clane')
        self.assertEqual(request['URL1'], 'http://diehard.tv:8080/john/mc')
        self.assertEqual(request['URL2'], 'http://diehard.tv:8080/john')
        self.assertEqual(request['URL3'], 'http://diehard.tv:8080')
        self.assertRaises(KeyError, request.get, 'URL4')

    def test_urlpath(self):
        # URLPATH0, etc. works the same as URL0, etc., except that the
        # URL scheme and server name aren't included, just the path
        # part.  This is the equivalent of calling request.getURL(n,
        # True) for zope.publisher's request.
        request = self.makeRequest()
        self.assertEqual(request['URLPATH0'], '/john/mc/clane')
        self.assertEqual(request['URLPATH1'], '/john/mc')
        self.assertEqual(request['URLPATH2'], '/john')
        self.assertEqual(request['URLPATH3'], '')
        self.assertRaises(KeyError, request.get, 'URLPATH4')

    def test_base(self):
        # XXX I have no idea what BASE does... help?
        request = self.makeRequest()
        self.assertEqual(request['BASE0'], 'http://diehard.tv:8080/john/mc')
        self.assertEqual(request['BASE1'],
                         'http://diehard.tv:8080/john/mc/clane')
        self.assertRaises(KeyError, request.get, 'BASE2')

    def test_basepath(self):
        # XXX I have no idea what BASEPATH does... help?
        request = self.makeRequest()
        self.assertEqual(request['BASEPATH0'], '/john/mc')
        self.assertEqual(request['BASEPATH1'], '/john/mc/clane')
        self.assertRaises(KeyError, request.get, 'BASEPATH2')

    def test_response(self):
        # A request's response is typically available as
        # request.response.  However, for legacy reasons, ZPublisher
        # also supports request.RESPONSE as well as
        # request['RESPONSE'].  We make sure both are supported here.
        request = self.makeRequest()
        self.assert_(request.get('RESPONSE') is not None)
        self.assert_(getattr(request, 'RESPONSE', None) is not None)

    def test_getattr(self):
        # The ZPublisher's HTTPRequest also allows access to
        # environment variables via attribute access (I know, it
        # sucks).
        request = self.makeRequest()
        self.assertEqual(request.PATH_INFO, '/john/mc/clane')

        # Note that URL is a bit of a special
        # fellow... zope.publisher's request.URL is a class property
        # that supports a __str__ method.  In five.publisher, we
        # really need it to be a string.
        self.assertEqual(request.URL, 'http://diehard.tv:8080/john/mc/clane')
        self.assertEqual(request.URL[:17], 'http://diehard.tv')

    def test_body(self):
        pass # TODO

    def test_form(self):
        # Both ZPublisher's and zope.publisher's request offer a
        # request.form dictionary which contains request input
        # specifically from GET or POST forms
        request = self.makeRequest()
        self.assertEqual(request.form['gun'], 'reload')
        self.assertEqual(request.form['terrorist'], 'kill')
        self.assert_(request.form.get('CONTENT_TYPE') is None)

    def test_cookies(self):
        pass # TODO

    def test_other(self):
        pass # TODO

class TestPublication(object):

    def getDefaultTraversal(self, request, ob):
        return ob, ()

    def callTraversalHooks(self, request, ob):
        pass

    def traverseName(self, request, ob, name):
        return ob

class FivePublicationTestEnvironment(CleanUp, TestEnvironment):

    def setUp(self):
        super(FivePublicationTestEnvironment, self).setUp()
        zope.component.provideAdapter(HTTPCharsets)

    def makeRequest(self):
        request = BrowserRequest(StringIO(''), test_environ.copy())
        # Set up request.form, etc.
        request.processInputs()
        # Make sure the URLs are set up correctly by faking traversal
        request.setPublication(TestPublication())
        request.traverse(object())
        return request

class ZPublisherTestEnvironment(TestEnvironment):

    def makeRequest(self):
        response = HTTPResponse()
        request = HTTPRequest(StringIO(''), test_environ.copy(),
                              response)
        # Set up request.form, etc.
        request.processInputs()
        # Make sure the URLs are set up correctly by faking traversal
        request['PARENTS'] = [object()]
        request.traverse('')
        return request

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ZPublisherTestEnvironment))
    suite.addTest(unittest.makeSuite(FivePublicationTestEnvironment))
    return suite

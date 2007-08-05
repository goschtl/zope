import unittest
from StringIO import StringIO
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from five.publication.request import BrowserRequest

environ = {
    'HTTP_COOKIE': 'tree-s=eJzT0MgpMOQKVneEA1dbda4CI67EkgJjLj0AeGcHew',
    'SCRIPT_NAME': '/john/mc/clane',
    'REQUEST_METHOD': 'GET',
    'PATH_INFO': '/john/mc/clane',
    'SERVER_PROTOCOL': 'HTTP/1.1',
    'QUERY_STRING': '',
    'CONTENT_LENGTH': '0',
    'SERVER_NAME': 'diehard.tv',
    'REMOTE_ADDR': '127.0.0.1',
    'SERVER_PORT': '8080',
    'CONTENT_TYPE': '',
    'HTTP_ACCEPT_CHARSET': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'HTTP_CONNECTION': 'keep-alive',
    'HTTP_HOST': 'diehard.tv:8080',
    'HTTP_ACCEPT': 'application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,*/*;q=0.5',
    'HTTP_ACCEPT_LANGUAGE': 'en-us,en;q=0.5',
    'HTTP_ACCEPT_ENCODING': 'gzip,deflate',
    'HTTP_KEEP_ALIVE': '300'
    }

class TestEnvironment(unittest.TestCase):

    def setUp(self):
        pass

    def test_url(self):
        request = self.makeRequest()
        self.assertEqual(request['URL'], 'http://diehard.tv:8080/john/mc/clane')
        self.assertEqual(request['URL0'], 'http://diehard.tv:8080/john/mc/clane')
        self.assertEqual(request['URL1'], 'http://diehard.tv:8080/john/mc')
        self.assertEqual(request['URL2'], 'http://diehard.tv:8080/john')
        self.assertEqual(request['URL3'], 'http://diehard.tv:8080')
        self.assertRaises(KeyError, request.get, 'URL4')

    def test_urlpath(self):
        request = self.makeRequest()
        self.assertEqual(request['URLPATH0'], '/john/mc/clane')
        self.assertEqual(request['URLPATH1'], '/john/mc')
        self.assertEqual(request['URLPATH2'], '/john')
        self.assertEqual(request['URLPATH3'], '')
        self.assertRaises(KeyError, request.get, 'URLPATH4')

    def test_base(self):
        request = self.makeRequest()
        self.assertEqual(request['BASE0'], 'http://diehard.tv:8080/john/mc')
        self.assertEqual(request['BASE1'],
                         'http://diehard.tv:8080/john/mc/clane')
        self.assertRaises(KeyError, request.get, 'BASE2')

    def test_basepath(self):
        request = self.makeRequest()
        self.assertEqual(request['BASEPATH0'], '/john/mc')
        self.assertEqual(request['BASEPATH1'], '/john/mc/clane')
        self.assertRaises(KeyError, request.get, 'BASEPATH2')

    def test_response(self):
        request = self.makeRequest()
        self.assert_(request.get('RESPONSE') is not None)
        self.assert_(getattr(request, 'RESPONSE', None) is not None)

class FivePublicationTestEnvironment(TestEnvironment):

    def makeRequest(self):
        return BrowserRequest(StringIO(''), environ.copy())

class ZPublisherTestEnvironment(TestEnvironment):

    def makeRequest(self):
        response = HTTPResponse()
        request = HTTPRequest(StringIO(''), environ.copy(), response)
        # This dance is sadly necessary to get the request's
        # environment set up correctly
        request['PARENTS'] = [object()]
        request.traverse('')
        return request

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ZPublisherTestEnvironment))
    suite.addTest(unittest.makeSuite(FivePublicationTestEnvironment))
    return suite

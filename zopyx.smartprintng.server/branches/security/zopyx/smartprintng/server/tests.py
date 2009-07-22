##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import base64
import xmlrpclib
import unittest
import zipfile
import tempfile
from repoze.bfg import testing

xml = """<?xml version="1.0"?>
<methodCall>
   <methodName>ping</methodName>
</methodCall>
"""
xml2 = """<?xml version="1.0"?>
<methodCall>
   <methodName>convertZIP</methodName>
    %s
</methodCall>
"""

class ViewTests(unittest.TestCase):

    """ These tests are unit tests for the view.  They test the
    functionality of *only* the view.  They register and use dummy
    implementations of repoze.bfg functionality to allow you to avoid
    testing 'too much'"""

    def setUp(self):
        """ cleanUp() is required to clear out the application registry
        between tests (done in setUp for good measure too)
        """
        testing.cleanUp()

    def tearDown(self):
        """ cleanUp() is required to clear out the application registry
        between tests
        """
        testing.cleanUp()

    def test_index(self):
        from zopyx.smartprintng.server.views import index
        context = testing.DummyModel()
        request = testing.DummyRequest()
        renderer = testing.registerDummyRenderer('templates/index.pt')
        response = index(context, request)
        renderer.assert_(project='zopyx.smartprintng.server')


class ViewIntegrationTests(unittest.TestCase):
    """ These tests are integration tests for the view.  These test
    the functionality the view *and* its integration with the rest of
    the repoze.bfg framework.  They cause the entire environment to be
    set up and torn down as if your application was running 'for
    real'.  This is a heavy-hammer way of making sure that your tests
    have enough context to run properly, and it tests your view's
    integration with the rest of BFG.  You should not use this style
    of test to perform 'true' unit testing as tests will run faster
    and will be easier to write if you use the testing facilities
    provided by bfg and only the registrations you need, as in the
    above ViewTests.
    """
    def setUp(self):
        """ This sets up the application registry with the
        registrations your application declares in its configure.zcml
        (including dependent registrations for repoze.bfg itself).
        """
        testing.cleanUp()
        import zopyx.smartprintng.server
        import zope.configuration.xmlconfig
        zope.configuration.xmlconfig.file('configure.zcml',
                                          package=zopyx.smartprintng.server)

    def tearDown(self):
        """ Clear out the application registry """
        testing.cleanUp()

    def test_index(self):
        from zopyx.smartprintng.server.views import index
        context = testing.DummyModel()
        request = testing.DummyRequest()
        result = index(context, request)
        self.assertEqual(result.status, '200 OK')
        body = result.app_iter[0]
        self.assertEqual(len(result.headerlist), 2)
        self.assertEqual(result.headerlist[0],
                         ('Content-Type', 'text/html; charset=UTF-8'))
        self.assertEqual(result.headerlist[1], ('Content-Length',
                                                str(len(body))))

    def test_xmlrpc_ping(self):
        from zopyx.smartprintng.server.views import ping
        context = testing.DummyModel()
        headers = dict()
        headers['content-type'] = 'text/xml'
        request = testing.DummyRequest(headers=headers, post=True)
        request.body = xml
        result = ping(context, request)
        self.assertEqual(result.status, '200 OK')
        body = result.app_iter[0]
        params, methodname = xmlrpclib.loads(result.body)
        self.assertEqual(params[0], 'zopyx.smartprintng.server')

    def test_xmlrpc_convertZIP(self):
        from zopyx.smartprintng.server.views import convertZIP
        context = testing.DummyModel()
        headers = dict()
        headers['content-type'] = 'text/xml'
        request = testing.DummyRequest(headers=headers, post=True)
        zip_archive = os.path.join(os.path.dirname(__file__), 'test_data', 'test.zip')
        zip_data = file(zip_archive, 'rb').read()
        params = xmlrpclib.dumps((base64.encodestring(zip_data), 'pdf-prince'))
        request.body = xml2 % params
        result = convertZIP(context, request)
        self.assertEqual(result.status, '200 OK')
        body = result.app_iter[0]
        params, methodname = xmlrpclib.loads(result.body)
        output_zipdata = base64.decodestring(params[0])
        output_zip_filename = tempfile.mktemp()
        file(output_zip_filename, 'wb').write(output_zipdata)
        ZIP = zipfile.ZipFile(output_zip_filename, 'r')
        self.assertEqual('output.pdf' in ZIP.namelist(), True)


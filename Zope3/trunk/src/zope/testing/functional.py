"""Functional testing framework for Zope 3.

There should be a file 'ftesting.zcml' in the current directory.

$Id: functional.py,v 1.2 2003/04/14 13:24:10 mgedmin Exp $
"""

import unittest
import sys
import traceback
from cStringIO import StringIO

from transaction import get_transaction
from zodb.db import DB
from zodb.storage.memory import MemoryFullStorage
from zodb.storage.demo import DemoStorage
from zope.app import Application
from zope.app.publication.zopepublication import ZopePublication
from zope.app.traversing import traverse
from zope.publisher.browser import BrowserRequest
from zope.publisher.publish import publish
import logging


class ResponseWrapper:
    """A wrapper that adds several introspective methods to a response."""

    def __init__(self, response, outstream, path):
        self._response = response
        self._outstream = outstream
        self._path = path

    def getOutput(self):
        """Returns the full HTTP output (headers + body)"""
        return self._outstream.getvalue()

    def getBody(self):
        """Returns the response body"""
        output = self._outstream.getvalue()
        idx = output.find('\n\n')
        if idx == -1:
            return None
        else:
            return output[idx+2:]

    def getPath(self):
        """Returns the path of the request"""
        return self._path

    def __getattr__(self, attr):
        return getattr(self._response, attr)


class FunctionalTestSetup:
    """Keeps shared state across several functional test cases."""

    __shared_state = { '_init': False }

    def __init__(self, config_file=None):
        """Initializes Zope 3 framework.

        Creates a volatile memory storage.  Parses Zope3 configuration files.
        """
        self.__dict__ = self.__shared_state

        if not self._init:
            if not config_file:
                config_file = 'ftesting.zcml'
            self.log = StringIO()
            # Make it silent but keep the log available for debugging
            logging.root.addHandler(logging.StreamHandler(self.log))
            self.base_storage = MemoryFullStorage("Memory Storage")
            self.db = DB(self.base_storage)
            self.app = Application(self.db, config_file)
            self.connection = None
            self._config_file = config_file
            self._init = 1
        elif config_file and config_file != self._config_file:
            # Running different tests with different configurations is not
            # supported at the moment
            raise NotImplementedError('Already configured'
                                      ' with a different config file')

    def setUp(self):
        """Prepares for a functional test case."""
        # Tear down the old demo storage (if any) and create a fresh one
        self.db.close()
        storage = DemoStorage("Demo Storage", self.base_storage)
        self.db = self.app.db = DB(storage)
        # Get hold of the root folder
        self.connection = self.db.open()
        root = self.connection.root()
        self.root_folder = root[ZopePublication.root_name]

    def tearDown(self):
        """Cleans up after a functional test case."""
        get_transaction().abort()
        if self.connection:
            self.connection.close()
            self.connection = None

    def getRootFolder(self):
        """Returns the Zope root folder."""
        return self.root_folder

    def getApplication(self):
        """Returns the Zope application instance."""
        return self.app


class FunctionalTestCase(unittest.TestCase):
    """Functional test case."""

    def setUp(self):
        """Prepares for a functional test case."""
        unittest.TestCase.setUp(self)
        FunctionalTestSetup().setUp()

    def tearDown(self):
        """Cleans up after a functional test case."""
        FunctionalTestSetup().tearDown()
        unittest.TestCase.tearDown(self)

    def getRootFolder(self):
        """Returns the Zope root folder."""
        return FunctionalTestSetup().getRootFolder()


class BrowserTestCase(FunctionalTestCase):
    """Functional test case for Browser requests."""

    def makeRequest(self, path='', basic=None, form=None, env={},
                    outstream=None):
        """Creates a new request object.

        Arguments:
          path   -- the path to be traversed (e.g. "/folder1/index.html")
          basic  -- basic HTTP authentication credentials ("user:password")
          form   -- a dictionary emulating a form submission
                    (Note that field values should be Unicode strings)
          env    -- a dictionary of additional environment variables
                    (You can emulate HTTP request header
                       X-Header: foo
                     by adding 'HTTP_X_HEADER': 'foo' to env)
          outstream -- a stream where the HTTP response will be written
        """
        if outstream is None:
            outstream = StringIO()
        environment = {"HTTP_HOST": 'localhost',
                       "HTTP_REFERER": 'localhost'}
        environment.update(env)
        app = FunctionalTestSetup().getApplication()
        request = app._request(path, '', outstream,
                               environment=environment,
                               basic=basic, form=form,
                               request=BrowserRequest)
        return request

    def publish(self, path, basic=None, form=None, env={}, handle_errors=False):
        """Renders an object at a given location.

        Arguments are the same as in makeRequest with the following exception:
          handle_errors  -- if False (default), exceptions will not be caught
                            if True, exceptions will return a formatted error
                            page.

        Returns the response object enhanced with the following methods:
          getOutput()    -- returns the full HTTP output as a string
          getBody()      -- returns the full response body as a string
          getPath()      -- returns the path used in the request
        """
        outstream = StringIO()
        request = self.makeRequest(path, basic=basic, form=form, env=env,
                                   outstream=outstream)
        response = ResponseWrapper(request.response, outstream, path)
        publish(request, handle_errors=handle_errors)
        return response

    def checkForBrokenLinks(self, body, path):
        """Looks for broken links in a page by trying to traverse relative
        URIs.
        """
        if not body: return
        from htmllib import HTMLParser
        from formatter import NullFormatter
        parser = HTMLParser(NullFormatter())
        parser.feed(body)
        parser.close()

        root = self.getRootFolder()
        base = path
        if not base.startswith('/'):
            base = '/' + base
        while not base.endswith('/'):
            base = base[:-1]
        errors = []
        for a in parser.anchorlist:
            if a.startswith('http://localhost/'):
                a = a[len('http://localhost/') - 1:]
            elif a.find(':') != -1:
                # XXX assume it is "proto:someuri"
                continue
            elif not a.startswith('/'):
                a = base + a
            if a.find('#') != -1:
                a = a[:a.index('#') - 1]
            rq = self.makeRequest()
            try:
                rq.traverse(a)
            except (KeyError, NameError, AttributeError):
                e = traceback.format_exception_only(*sys.exc_info()[:2])[-1]
                errors.append((a, e.strip()))
        if errors:
            self.fail("%s contains broken links:\n" % path
                      + "\n".join(["  %s:\t%s" % (a, e) for a, e in errors]))

#
# Sample functional test case
#

class SampleFunctionalTest(BrowserTestCase):

    def testRootPage(self):
        response = self.publish('/')
        self.assertEquals(response.getStatus(), 200)

    def testRootPage_preferred_languages(self):
        response = self.publish('/', env={'HTTP_ACCEPT_LANGUAGE': 'en'})
        self.assertEquals(response.getStatus(), 200)

    def testNotExisting(self):
        response = self.publish('/nosuchthing', handle_errors=1)
        self.assertEquals(response.getStatus(), 404)

    def testLinks(self):
        response = self.publish('/')
        self.assertEquals(response.getStatus(), 200)
        self.checkForBrokenLinks(response.getBody(), response.getPath())


def sample_test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SampleFunctionalTest))
    return suite


if __name__ == '__main__':
    unittest.main()

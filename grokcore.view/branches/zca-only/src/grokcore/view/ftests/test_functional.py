# -*- coding: utf-8 -*-

import doctest
import grokcore.component
import grokcore.view
import os.path
import re
import types
import unittest
import webob.dec

from cromlech.bootstrap.testlayer import ZODBLayer
from persistent.interfaces import IPersistent
from pkg_resources import resource_listdir
from zope.component import getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.publisher.interfaces import IRequest, IPublication
from zope.publisher.publish import publish
from zope.site.interfaces import IRootFolder
from zope.site.folder import rootFolder


ROOT = 'grok'

@grokcore.component.implementer(IRootFolder)
@grokcore.component.adapter(IPersistent, types.BooleanType)
def test_root(db_root, creation=False):
    folder = db_root.get(ROOT, None)
    if folder is None and creation is True:
        folder = rootFolder()
        notify(ObjectCreatedEvent(folder))
        db_root[ROOT] = folder
    return folder


class WSGIApplication(object):

    def __init__(self, db):
        self.db = db

    @webob.dec.wsgify
    def __call__(self, webob_req):

        # We want an interaction here
        # XXXX

        # We get a valid zope request
        request = IRequest(webob_req)

        # Here, we keep the zope compatibility. It will go away
        request.setPublication(getMultiAdapter(
            (request, self.db), IPublication))

        # publishing
        response = publish(request)

        # Return the WSGI server response
        return response


class BrowserLayer(ZODBLayer):
    """This create a test layer with a test database and register a wsgi
    application to use that test database.

    A wsgi_intercept handler is installed as well, so you can use a
    WSGI version of zope.testbrowser Browser instance to access the
    application.
    """

    def testSetUp(self):
        ZODBLayer.testSetUp(self)
        self.application = WSGIApplication(self.db)

    def getApplication(self):
        return self.application


FunctionalLayer = BrowserLayer(grokcore.view)


def suiteFromPackage(name):
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()

    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'grokcore.view.ftests.%s.%s' % (name, filename[:-3])
        test = doctest.DocTestSuite(
            dottedname,
            extraglobs=dict(
                getRootFolder=FunctionalLayer.getRootFolder,
                getApplication=FunctionalLayer.getApplication),
            optionflags=(doctest.ELLIPSIS+
                         doctest.NORMALIZE_WHITESPACE+
                         doctest.REPORT_NDIFF),
            )
        test.layer = FunctionalLayer

        suite.addTest(test)
    return suite


def test_suite():
    suite = unittest.TestSuite()
    for name in ['view', 'staticdir', 'url']:
        suite.addTest(suiteFromPackage(name))
    return suite

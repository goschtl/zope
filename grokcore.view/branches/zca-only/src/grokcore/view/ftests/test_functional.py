# -*- coding: utf-8 -*-

import doctest
import grokcore.component
import grokcore.view
import os.path
import re
import types
import unittest
import webob
import webob.dec
import transaction

from cromlech.dawnlight.publish import DawnlightPublisher
from cromlech.io.interfaces import IRequest, IPublisher
from zope.component.testlayer import ZCMLFileLayer
from cromlech.dawnlight import IDawnlightApplication
import zope.component
from zope.component import hooks
from pkg_resources import resource_listdir
from zope.component import getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.publisher.publish import publish
from zope.site.interfaces import IRootFolder
from zope.site.folder import rootFolder
from zope.interface import implements, Interface
from zope.security.interfaces import IGroupAwarePrincipal
from zope.security.testing import Participation
from zope.security.management import newInteraction, endInteraction
from zope.component.interfaces import ISite
from zope.site.site import LocalSiteManager


class IUnauthenticatedPrincipal(IGroupAwarePrincipal):
    pass


class UnauthenticatedPrincipal(object):
    implements(IUnauthenticatedPrincipal)

    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description
        self.groups = ["zope.Anybody"]


unauthenticated_principal = UnauthenticatedPrincipal(
    'test.unauthenticated',
    'Unauthenticated principal',
    'The default unauthenticated principal.')


class Interaction(object):

    def __init__(self, user):
        self.user = user

    def __enter__(self):
        participation = Participation(self.user)
        newInteraction(participation)
        return participation

    def __exit__(self, type, value, traceback):
        endInteraction()


class SitePublisher(object):

    def __init__(self, request, app, site):
        self.app = app
        self.request = request
        self.site = site

    def __enter__(self):
        publisher = DawnlightPublisher(self.request, self.app)

        if not ISite.providedBy(self.site):
            site_manager = LocalSiteManager(self.site)
            self.site.setSiteManager(site_manager)

        zope.component.hooks.setSite(self.site)
        return publisher

    def __exit__(self, type, value, traceback):
        zope.component.hooks.setSite()


SITE = rootFolder()

class WSGIApplication(object):
    implements(IDawnlightApplication)

    def __init__(self, user):
        self.user = user

    @webob.dec.wsgify
    def __call__(self, req):
        request = getMultiAdapter((req, self), IRequest)
        with Interaction(self.user) as participation:             
            with SitePublisher(request, self, SITE) as publisher:
                response = publisher.publish(SITE, handle_errors=False)
        return response


class BrowserLayer(ZCMLFileLayer):
    """This create a test layer with a test database and register a wsgi
    application to use that test database.

    A wsgi_intercept handler is installed as well, so you can use a
    WSGI version of zope.testbrowser Browser instance to access the
    application.
    """

    def testSetUp(self):
        ZCMLFileLayer.testSetUp(self)
        zope.component.hooks.setHooks()
        self.application = WSGIApplication

    def getRootFolder(self):
        return SITE

    def getApplication(self, user=unauthenticated_principal):
        return self.application(user)

    def testTearDown(self):
        SITE.data.clear()


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
    for name in ['view', 'url']:
        suite.addTest(suiteFromPackage(name))
    return suite

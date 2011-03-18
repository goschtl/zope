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

from cromlech.bootstrap.testlayer import ZODBLayer
from cromlech.bootstrap.helper import Bootstrapper
from persistent.interfaces import IPersistent
from pkg_resources import resource_listdir
from zope.component import getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.publisher.interfaces import IRequest, IPublication
from zope.publisher.publish import publish
from zope.site.interfaces import IRootFolder
from zope.site.folder import rootFolder
from zope.interface import implements, Interface
from zope.security.interfaces import IGroupAwarePrincipal
from zope.security.testing import Participation
from zope.security.management import newInteraction, endInteraction


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

ROOT = 'grok'

@grokcore.component.implementer(IRootFolder)
@grokcore.component.adapter(IPersistent, types.BooleanType)
def test_root(db_root, creation=False):
    print "Creation of ROOT : %s" % creation
    folder = db_root.get(ROOT, None)
    if folder is None and creation is True:
        folder = rootFolder()
        notify(ObjectCreatedEvent(folder))
        db_root[ROOT] = folder
    return folder



def getUser(wsgiapp, app, request):
    request.setPrincipal(unauthenticated_principal)
    return unauthenticated_principal


class Interaction(object):

    def __init__(self, user, request):
 

    def __enter__(self):
        participation = Participation(unauthenticated_principal)
        newInteraction(participation)
        return participation

    def __exit__(self, type, value, traceback):
        endInteraction()
        if traceback is not None:
            logger.warn(value)


class WSGIApplication(object):

    def __init__(self, db):
        self.db = db

    @webob.dec.wsgify
    def __call__(self, webob_req):

        request = IRequest(webob_req)

        with Bootstrapper(self.db) as root, app:
            with transaction:
                user = setUser(self, app, request)
                with Interaction(user) as participation:
                    response = publish(request, root=app, handle_errors=False)

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
    for name in ['view', 'url']:
        suite.addTest(suiteFromPackage(name))
    return suite

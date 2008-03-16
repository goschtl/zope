##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
$Id$
"""
__docformat__ = "reStructuredText"

from cStringIO import StringIO
import unittest
import zope.interface
import zope.schema

from zope.testing import doctest
from zope.interface import implements
from zope.component import provideUtility, provideAdapter
from zope.publisher.interfaces import IRequest
from zope.publisher.http import HTTPRequest
from zope.testing import doctestunit

from zope.app.component import hooks
from zope.app.component.interfaces import ISite
from zope.app.testing import functional
from zope.app.testing import placelesssetup
from zope.app.testing import setup
from zope.app.testing import ztapi
from zope.app.session.interfaces import IClientId
from zope.app.session.interfaces import IClientIdManager
from zope.app.session.interfaces import ISession
from zope.app.session.interfaces import ISessionDataContainer
from zope.app.session.session import ClientId
from zope.app.session.session import Session
from zope.app.session.session import PersistentSessionDataContainer
from zope.app.session.http import CookieClientIdManager

from z3c.configurator import configurator
from z3c.authentication.cookie import interfaces
from z3c.authentication.cookie import session


###############################################################################
#
# Test Component
#
###############################################################################
from zope.app.folder.folder import Folder
from z3c.authentication.cookie.configurator import SetUpCookieCredentialsPlugin

class ISiteStub(zope.interface.Interface):
    """Configurator marker interface."""


class SiteStub(Folder):
    """A new site providing IMySite."""
    zope.interface.implements(ISiteStub) 

class MakeSiteDuringMySiteAdding(configurator.ConfigurationPluginBase):
    """Configurator which does make a site from a folder."""
    zope.component.adapts(ISiteStub)

    def __call__(self, data):
        if not ISite.providedBy(self.context):
            sm = LocalSiteManager(self.context)
            self.context.setSiteManager(sm)
        hooks.setSite(self.context)
        sm = zope.component.getSiteManager(self.context)


class SiteStubPlugin(SetUpCookieCredentialsPlugin):
    zope.component.adapts(ISiteStub)


# add form for SiteStub (ftesting)
from zope.formlib import form

class SiteStubAddForm(form.AddForm):
    """Recruiter Site Add Form, only available for zope.Manager."""
    form_fields = form.Fields(
        zope.schema.TextLine(__name__='__name__', title=u'Name'),)

    def createAndAdd(self, data):
        # get form data
        name = data.get('__name__', u'')

        # Add the site
        obj = SiteStub()
        self.context[name] = obj

        # Configure the new site
        configurator.configure(obj, data)

        self._finished_add = True
        return obj

    def nextURL(self):
        return self.request.URL[-1]


###############################################################################
#
# testing helper
#
###############################################################################

def getRootFolder():
    return functional.FunctionalTestSetup().getRootFolder()


class TestClientId(object):
    implements(IClientId)
    def __new__(cls, request):
        return 'dummyclientidfortesting'


###############################################################################
#
# placefulSetUp
#
###############################################################################

def siteSetUp(test):
    site = setup.placefulSetUp(site=True)
    test.globs['rootFolder'] = site
    zope.component.provideAdapter(MakeSiteDuringMySiteAdding, name='make site')
    zope.component.provideAdapter(SiteStubPlugin, name='setup ')


def siteTearDown(test):
    setup.placefulTearDown()


def sessionSetUp():
    # setup client ids
    ztapi.provideAdapter(IRequest, IClientId, TestClientId)
    ztapi.provideAdapter(IRequest, interfaces.ILifeTimeClientId, TestClientId)

    # setup session adapters
    ztapi.provideAdapter(IRequest, ISession, Session)
    ztapi.provideAdapter(IRequest, interfaces.ILifeTimeSession, 
        session.LifeTimeSession)

    # setup client id managers
    ztapi.provideUtility(IClientIdManager, CookieClientIdManager())
    ccim = CookieClientIdManager()
    ccim.cookieLifetime = 0
    ztapi.provideUtility(IClientIdManager, ccim, 
        name='LifeTimeSessionClientIdManager')

    # setup session data containers
    defaultSDC = PersistentSessionDataContainer()
    ztapi.provideUtility(ISessionDataContainer, defaultSDC, '')
    cookieSDC = session.CookieCredentialSessionDataContainer()
    ztapi.provideUtility(ISessionDataContainer, cookieSDC, 
        interfaces.SESSION_KEY)


def clientIdSetUp():
    placelesssetup.setUp()
    sessionSetUp()
    request = HTTPRequest(StringIO(), {}, None)
    return request


def clientIdTearDown():
    placelesssetup.tearDown()


functional.defineLayer("Z3cAuthenticationCookieLayer", "testlayer.zcml")


def FunctionalDocFileSuite(path, **kw):
    """Including relative path setup."""
    globs = {'getRootFolder': getRootFolder}
    if 'globs' in kw:
        globs.update(kw['globs'])
        del kw['globs']

    if 'package' not in kw:
        kw['package'] = doctest._normalize_module(kw.get('package', None))
    kw['module_relative'] = kw.get('module_relative', True)

    suite = functional.FunctionalDocFileSuite(
            path,
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
            globs=globs,
            **kw)
    suite.layer = Z3cAuthenticationCookieLayer
    return suite

##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
import logging
import time

from zope import interface
from zope import component
from zope import event

from zope.component.interfaces import IFactory
from zope.security.checker import ProxyFactory
from zope.publisher.browser import BrowserRequest
from zope.error.interfaces import IErrorReportingUtility
from zope.error.error import RootErrorReportingUtility
from zope.lifecycleevent import ObjectCreatedEvent
from zope.app.applicationcontrol.applicationcontrol \
     import applicationControllerRoot

from zope.app.component import hooks
from zope.app.publication.browser import BrowserPublication
from zope.app.publication.interfaces import (
        IRequestPublicationFactory,
        IBrowserRequestFactory,
        )
from zope.app.component.site import LocalSiteManager
from zope.app.folder.interfaces import IRootFolder
from zope.app.component.site import SiteManagerContainer
from zope.app.container.contained import setitem

from interfaces import IConfig, IConfigurableSite, NoZODBStarted


class App(dict, SiteManagerContainer):
    interface.implements(IRootFolder)

    def __init__(self):
        t = time.time()
        sm = LocalSiteManager(self)
        self.setSiteManager(sm)
        hooks.setSite(self)
        eru = RootErrorReportingUtility()
        event.notify(ObjectCreatedEvent(eru))
        sm['errors'] = eru
        sm.registerUtility(eru, IErrorReportingUtility)
        self.setUpSites()
        logging.info('Set up root Application %s' % (time.time()-t))
        event.notify(NoZODBStarted(self))

    def setUpSites(self):
        config = component.getUtility(IConfig)
        for name, sc in config.sites.items():
            factory = sc.get('factory')
            factory = component.getUtility(IFactory, factory)
            obj = factory()
            if not IConfigurableSite.providedBy(obj):
                interface.alsoProvides(obj, IConfigurableSite)
            event.notify(ObjectCreatedEvent(obj))
            setitem(self, self.__setitem__, name, obj)
            logging.info('Set up site %r' % name)

    def __repr__(self):
        return "<%s>" % self.__class__.__name__


class NoZODBPublication(BrowserPublication):

    def __init__(self):
        app = ProxyFactory(App())
        event.notify(ObjectCreatedEvent(app))
        self._app = app

    def getApplication(self, request):
        stack = request.getTraversalStack()
        if '++etc++process' in stack:
            return applicationControllerRoot
        return self._app


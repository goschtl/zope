# -*- coding: utf-8 -*-

import zope.component
from zope.component.interfaces import IComponentLookup
from zope.component.testlayer import ZCMLFileLayer
from zope.container import btree
from zope.container.interfaces import ISimpleReadContainer
from zope.container.traversal import ContainerTraversable
from zope.interface import Interface
from zope.site.folder import rootFolder
from zope.site.site import LocalSiteManager, SiteManagerAdapter
from zope.traversing.interfaces import ITraversable
from zope.traversing.testing import setUp as traversingSetUp
from zope.configuration.config import ConfigurationMachine
from grokcore.component import zcml

from zope.component import provideHandler, getGlobalSiteManager
from zope.session.interfaces import IClientId, IClientIdManager, ISession
from zope.session.interfaces import ISessionDataContainer
from zope.session.interfaces import ISessionPkgData, ISessionData
from zope.session.session import ClientId, Session
from zope.session.session import PersistentSessionDataContainer
from zope.session.session import RAMSessionDataContainer
from zope.session.http import CookieClientIdManager
from zope.publisher.interfaces import IRequest


class MegrokLayoutLayer(ZCMLFileLayer):
    
    def setUp(self):
        ZCMLFileLayer.setUp(self)
    
        # Set up site manager adapter
        zope.component.provideAdapter(
            SiteManagerAdapter, (Interface,), IComponentLookup)
    
        # Set up traversal
        traversingSetUp()
        zope.component.provideAdapter(
            ContainerTraversable, (ISimpleReadContainer,), ITraversable)

        # Session
        zope.component.provideAdapter(ClientId, (IRequest,), IClientId)
        zope.component.provideAdapter(Session, (IRequest,), ISession)
        zope.component.provideUtility(CookieClientIdManager(), IClientIdManager)
        sdc = PersistentSessionDataContainer()
        zope.component.provideUtility(sdc, ISessionDataContainer, '')
    
        # Set up site
        site = rootFolder()
        site.setSiteManager(LocalSiteManager(site))
        zope.component.hooks.setSite(site)
        
        return site
    

    def tearDown(self):
        ZCMLFileLayer.tearDown(self)
        zope.component.hooks.resetHooks()
        zope.component.hooks.setSite()


def grok(module_name):
    config = ConfigurationMachine()
    zcml.do_grok('grokcore.component.meta', config)
    zcml.do_grok('grokcore.security.meta', config)
    zcml.do_grok('grokcore.view.meta', config)
    zcml.do_grok('grokcore.view.templatereg', config)
    zcml.do_grok(module_name, config)
    config.execute_actions()

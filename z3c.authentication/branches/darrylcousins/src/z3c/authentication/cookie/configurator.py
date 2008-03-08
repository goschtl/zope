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

import zope.component
import zope.interface
from zope.app.component.site import LocalSiteManager
from z3c import configurator
from zope.app.component import hooks
from zope.app.component.interfaces import ISite
import zope.event
from zope.lifecycleevent import ObjectCreatedEvent
from zope.app.authentication.interfaces import IPluggableAuthentication
from zope.app.authentication.authentication import PluggableAuthentication
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.app.security.interfaces import IAuthentication
from zope.app.session.interfaces import ISessionDataContainer
from zope.app.session.interfaces import IClientIdManager
from zope.app.session.http import CookieClientIdManager

from z3c.authentication.cookie import interfaces
from z3c.authentication.cookie.plugin import CookieCredentialsPlugin
from z3c.authentication.cookie.session import \
    CookieCredentialSessionDataContainer


class SetUpCookieCredentialsPlugin(configurator.ConfigurationPluginBase):
    """Configurator adding a lifetime cookie session plugin."""

    def __call__(self, data):
        # first, make a site if no allready done
        if not ISite.providedBy(self.context):
            sm = LocalSiteManager(self.context)
            self.context.setSiteManager(sm)
        hooks.setSite(self.context)
        sm = zope.component.getSiteManager(self.context)

        # Add a liftime cookie credential to the PAU
        site = self.context
        sm = site.getSiteManager()
        default = sm['default']

        # add a PAU if not existent
        pau = None
        for item in default.values():
            if IPluggableAuthentication.providedBy(item):
                pau = item
        if pau is None:
            pau = PluggableAuthentication()
            zope.event.notify(ObjectCreatedEvent(pau))
            default['PluggableAuthentication'] = pau
            sm.registerUtility(pau, IAuthentication)

        # setup credentials plugin
        cred = CookieCredentialsPlugin()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(cred))
        pau[u'Z3C Cookie Credentials'] = cred
        pau.credentialsPlugins += (u'Z3C Cookie Credentials',)

        # setup cookie session data container
        ccsdc = CookieCredentialSessionDataContainer()
        # Expiry time of 0 means never (well - close enough)
        ccsdc.timeout = 0
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(ccsdc))
        default['CookieCredentialSessionDataContainer'] = ccsdc
        sm.registerUtility(ccsdc, ISessionDataContainer, 
            interfaces.SESSION_KEY)

        # setup lifetime session cookie client id manager
        ccim = CookieClientIdManager()
        # Expiry time of 0 means never (well - close enough)
        ccim.cookieLifetime = 0
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(ccim))
        default['LifeTimeSessionClientIdManager'] = ccim
        sm.registerUtility(ccim, IClientIdManager, 
            name='LifeTimeSessionClientIdManager')

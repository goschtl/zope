##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""ZSCP Web Site

$Id$
"""
__docformat__ = "reStructuredText"

from zope.schema.fieldproperty import FieldProperty
import zope.component
import zope.interface
import zope.interface

from zope.app import container
from zope.app import folder
from zope.app import security, zapi
from zope.app import zapi
from zope.app.authentication import principalfolder
from zope.app.authentication import authentication
from zope.app.component import site
from zope.app.component.interfaces import ISite
from zope.app.component.interfaces.registration import ActiveStatus
from zope.app.component.site import SiteManagementFolder
from zope.app.container.interfaces import INameChooser
from zope.app.event import objectevent
from zope.app.utility import UtilityRegistration

from zf.zscp.website import interfaces


class ZSCPSite(folder.folder.Folder):
    zope.interface.implements(interfaces.IZSCPSite)

    def __init__(self):
        super(ZSCPSite, self).__init__()
        self.setSiteManager(site.LocalSiteManager(self))

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


_marker = object()

def ensureUtility(site, name, interface, utility, package, key):
    """Add and return the utility."""
    # preconditions
    name = unicode(name)

    if not ISite.providedBy(site):
        raise TypeError('ISite required.')

    # get or create sitemanagement folder (package)
    sitemanager = site.getSiteManager()
    try:
        default = sitemanager[package]
    except:
        sitemanager[package] = SiteManagementFolder()
        default = sitemanager[package]

    # choose class name as key if not given
    if key == _marker:
        chooser = container.interfaces.INameChooser(default)
        key = chooser.chooseName(utility.__name__, utility)

    # add utility to sitemanagement folder
    default[key] = utility

    # register utility
    path = zapi.getPath(utility)
    registration = UtilityRegistration(name, interface, utility)
    choosenkey = default.registrationManager.addRegistration(registration)
    component = zapi.traverse(default.registrationManager, choosenkey)
    component.status = ActiveStatus

    return zapi.traverse(sitemanager, path)


# plugable authentication utility
def addPluggableAuthentication(site, name='', package='default', key=_marker, 
    prefix=''):
    """Add a plugable authentication utility (pau) to a site

    The pau is added to the package and activated.
    This assumes the site has already a Utility Service.
    """

    interface = security.interfaces.IAuthentication
    utility = authentication.PluggableAuthentication(prefix)

    return ensureUtility(site, name, interface, utility, package, key)



# add authenticator plugin
def addAuthenticatorPlugin(pau, key, utility, name):
    """Add authenticator plugin."""

    pau.authenticatorPlugins += (name,)
    package = pau.__name__
    interface = authentication.interfaces.IAuthenticatorPlugin

    return ensureAuthenticationPlugin(pau, name, interface, utility, key)


def ensureAuthenticationPlugin(pau, name, interface, utility, key):
    """Add and return the utility."""
    # preconditions
    name = unicode(name)

    # choose class name as key if not given
    if key == _marker:
        chooser = INameChooser(default)
        key = chooser.chooseName(utility.__name__, utility)

    # add utility to sitemanagement folder
    pau[key] = utility

    # register utility
    path = zapi.getPath(utility)
    registration = UtilityRegistration(name, interface, utility)
    choosenkey = pau.registrationManager.addRegistration(registration)
    component = zapi.traverse(pau.registrationManager, choosenkey)
    component.status = ActiveStatus

    return zapi.traverse(pau, path)



def addAuthenticationUtilityToSite(ob, event):
    """Add a pluggable authentication utility to the zscp site."""

    prefix = 'zscp.'
    pau = addPluggableAuthentication(ob)

    # setup 'principals' principal folder
    principals = principalfolder.PrincipalFolder(prefix)
    zope.event.notify(objectevent.ObjectCreatedEvent(principals))
    principals = addAuthenticatorPlugin(
        pau, u'principals', principals, u'principals')

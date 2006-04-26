##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

__docformat__ = 'restructuredtext'

from zope.app import zapi
from zope.app.container.interfaces import INameChooser
from zope.app.component.interfaces.registration import ActiveStatus
from zope.app.component.interfaces import IPossibleSite
from zope.app.component.interfaces import ISite
from zope.app.component.site import LocalSiteManager
from zope.app.utility import UtilityRegistration



def addSiteManager(possiblesite):
    """Extend a possible site to a site."""

    # preconditions
    if not IPossibleSite.providedBy(possiblesite) or ISite.providedBy(possiblesite):
        raise TypeError('IPossibleSite required.')

    # essentials
    sm = LocalSiteManager(possiblesite)
    possiblesite.setSiteManager(sm)



def addLocalUtility(site, name, iface, utility, package='default'):
    """Add a utility to a site

    The utility is added to the package and activated.
    This assumes the site has already a Utility Service.
    """
    # preconditions
    if not ISite.providedBy(site):
        raise TypeError('ISite required.')

    # get site manager and site management folder
    sitemanager = site.getSiteManager()
    default = sitemanager[package]

    # add utility to site management folder
    chooser = INameChooser(default)
    folder_name = chooser.chooseName(utility.__name__, utility)
    try: 
        default[folder_name] = utility
    except Exception, e:
        # TODO: raise exception
        print 'XXX', e # adapt to IReference Error

    # create service registration
    path = zapi.getPath(utility)
    registration = UtilityRegistration(name, iface, utility)
    key = default.registrationManager.addRegistration(registration)
    zapi.traverse(default.registrationManager, key).status = ActiveStatus  

    return zapi.traverse(sitemanager, path)

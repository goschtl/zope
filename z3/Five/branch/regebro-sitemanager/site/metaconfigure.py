##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Five-specific directive handlers

These directives are specific to Five and have no equivalents in Zope 3.

$Id: fiveconfigure.py 18581 2005-10-14 16:54:25Z regebro $
"""

from zope.interface import classImplements, classImplementsOnly, implementedBy
from zope.interface.interface import InterfaceClass
from zope.configuration.exceptions import ConfigurationError
from zope.app.component.metaconfigure import adapter
from zope.app.utility.interfaces import ILocalUtilityService
from zope.app.site.interfaces import IPossibleSite, ISite

from localsite import FiveSite, SimpleLocalUtilityService

def classSiteHook(class_, site_class):
    setattr(class_, 'getSiteManager',
            site_class.getSiteManager.im_func)
    setattr(class_, 'setSiteManager',
            site_class.setSiteManager.im_func)
 
count = 0
def next():
    global count
    count += 1
    return count

_localsite_monkies = []
def installSiteHook(_context, class_, site_class=None, utility_service=None):
    if site_class is None:
        if not IPossibleSite.implementedBy(class_):
            # This is not a possible site, we need to monkey-patch it so that
            # it is.
            site_class = FiveSite
    else:
        if not IPossibleSite.implementedBy(site_class):
            raise ConfigurationError('Site class does not implement '
                                     'IPossibleClass: %s' % site_class)
    if site_class is not None:
        _context.action(
            discriminator = (class_,),
            callable = classSiteHook,
            args=(class_, site_class)
            )
        _context.action(
            discriminator = (class_, IPossibleSite),
            callable = classImplements,
            args=(class_, IPossibleSite)
            )
    if utility_service is None:
        utility_service = SimpleLocalUtilityService
    else:
        if not ILocalUtilityService.implementedBy(utility_service):
            raise ConfigurationError('utility_service does not implement '
                                     'ILocalUtilityService: %s' % utility_service)
        
    # Generate a marker interface that should be unique, so that
    # we can register the utility service only for this class.
    iface = InterfaceClass('IFiveSite%s' % next())
    adapter(_context, factory=(utility_service,),
            provides=ILocalUtilityService,
            for_=(iface,))
    _context.action(
        discriminator = (class_, 'UtilityMarker'),
        callable = classImplements,
        args=(class_, iface)
        )
    _localsite_monkies.append(class_)

def uinstallSiteHooks():
    for class_ in _localsite_monkies:
        delattr(class_, 'getSiteManager')
        delattr(class_, 'setSiteManager')
        classImplementsOnly(class_, implementedBy(class_)-IPossibleSite)
        _localsite_monkies.remove(class_)
    
from zope.testing.cleanup import addCleanUp
addCleanUp(uinstallSiteHooks)
del addCleanUp


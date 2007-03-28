##############################################################################
#
# Copyright (c) 2004 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""site utils

$Id: utils.py 12899 2006-07-26 21:57:37Z benji $
"""
import zope.component.interfaces
import zope.app.container.interfaces
import zope.event
import zope.lifecycleevent
import zope.app.component.interfaces.registration

# from a site, to get to the default package, the incantation is
# site.getSiteManager()['default']

def addLocalUtility(package, utility, interface=None,
                    name='', name_in_container='', comment=u'',
                    registry=None):
    chooser = zope.app.container.interfaces.INameChooser(package)
    name_in_container = chooser.chooseName(name_in_container, utility)
    zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(utility))
    package[name_in_container] = utility
    # really want IComponentRegistry, but that is not set up in Zope 3 ATM
    if registry is None:
        registry = zope.component.interfaces.IComponentLookup(package)
    registry.registerUtility(utility, interface, name, comment)

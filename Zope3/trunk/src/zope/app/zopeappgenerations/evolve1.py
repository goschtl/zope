##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Evolve the ZODB from Zope X3.0 to a Zope X3.1 compatible format.

$Id$
"""
__docformat__ = "reStructuredText"
from zope.app.zopeappgenerations import getRootFolder
from zope.app.generations.utility import findObjectsProviding
from zope.app.registration.interfaces import IComponentRegistration
from zope.app.site.interfaces import ISite 

generation = 1

def evolve(context):
    """Evolve the ZODB from a Zope X3.0 to a X3.1 compatible format.

    - Component-based registrations used to keep track of their components via
      the component's path. Now it stores the component directly. All
      registrations are updated to this new format.
    """
    root = getRootFolder(context)

    # Fix up registration `componentPath` --> `component`
    sites = findObjectsProviding(root, ISite)
    for site in sites:
        registrations = findObjectsProviding(site.getSiteManager(),
                                             IComponentRegistration)
        for reg in registrations:
            if reg._BBB_componentPath is not None:
                reg.component = reg.getComponent()

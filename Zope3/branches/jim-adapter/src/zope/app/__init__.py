##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Zope application package.

$Id$
"""
##############################################################################
# BBB 2006/04/03 -- to be removed after 12 months

from zope.deferredimport import deprecatedModule

modules_aliases_35 = {
    'zope.app.decorator': 'zope.decorator',

    'zope.app.datetimeutils': 'zope.datetime',
    'zope.app.timezones': 'zope.datetime.timezones',

    'zope.app.size': 'zope.size',
    'zope.app.size.interfaces': 'zope.size.interfaces',

    'zope.app.traversing': 'zope.traversing',
    'zope.app.traversing.adapters': 'zope.traversing.adapters',
    'zope.app.traversing.api': 'zope.traversing.api',
    'zope.app.traversing.interfaces': 'zope.traversing.interfaces',
    'zope.app.traversing.browser': 'zope.traversing.browser',
    'zope.app.traversing.browser.absoluteurl':
        'zope.traversing.browser.absoluteurl',
    'zope.app.traversing.browser.interfaces':
        'zope.traversing.browser.absoluteurl',

    'zope.app.location': 'zope.location',
    'zope.app.location.interfaces': 'zope.location.interfaces',
    'zope.app.location.pickling': 'zope.location.pickling',
    'zope.app.locatin.traversing': 'zope.location.traversing',

    'zope.app.annotation': 'zope.annotation',
    'zope.app.annotation.attribute': 'zope.annotation.attribute',
    'zope.app.annotation.interfaces': 'zope.annotation.interfaces',

    'zope.app.event.objectevent': 'zope.lifecycleevent',
    'zope.app.event.interfaces': 'zope.lifecycleevent.interfaces',
    'zope.app.event.dispatch': 'zope.component.event',
    'zope.app.event.tests.placelesssetup': 'zope.component.testing',

    'zope.app.security.adapter': 'zope.security.adapter',
    'zope.app.component.interface': 'zope.component.interface',
    }

msg_35 = "%s has been moved to %s.  This alias will be removed in Zope 3.5."
for old, new in modules_aliases_35.iteritems():
    deprecatedModule(old, new, msg_35 % (old, new))

##############################################################################

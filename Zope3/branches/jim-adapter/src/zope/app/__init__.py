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

import sys
import zope.dottedname.resolve
from zope.deprecation import deprecated

modules_aliases_35 = {
    'zope.app.decorator': 'zope.decorator',

    'zope.app.datetimeutils': 'zope.datetime',
    'zope.app.timezones': 'zope.datetime.timezones',

    'zope.app.size': 'zope.size',
    'zope.app.size.interfaces': 'zope.size.interfaces',

#XXX disabled because of circular import problems; needs to be reenabled
#
#    'zope.app.traversing': 'zope.traversing',
#    'zope.app.traversing.adapters': 'zope.traversing.adapters',
#    'zope.app.traversing.api': 'zope.traversing.api',
#    'zope.app.traversing.interfaces': 'zope.traversing.interfaces',
#    'zope.app.traversing.browser': 'zope.traversing.browser',
#    'zope.app.traversing.browser.absoluteurl':
#        'zope.traversing.browser.absoluteurl',
#    'zope.traversing.browser.interfaces':
#        'zope.traversing.browser.absoluteurl',

#TODO provide BBB for zope.app.location
    }

msg_35 = "%s has been moved to %s.  This alias will be removed in Zope 3.5."
for old, new in modules_aliases_35.iteritems():
    newmodule = zope.dottedname.resolve.resolve(new)
    sys.modules[old] = deprecated(newmodule, msg_35 % (old, new))

##############################################################################

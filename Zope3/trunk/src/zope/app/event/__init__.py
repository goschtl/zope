##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Event Package

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.deferredimport
zope.deferredimport.deprecated(
    "Event support has been moved to zope.component.event, life cycle events "
    "to zope.lifecycleevent.  This reference will be gone in Zope 3.5",
    objectevent = 'zope.lifecycleevent',
    interfaces = 'zope.lifecycleevent.interfaces',
    dispatch = 'zope.component.event',
    )

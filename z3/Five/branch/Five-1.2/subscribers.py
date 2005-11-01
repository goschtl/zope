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
"""
Five subscriber definitions.

$Id$
"""
# The following are imported here because it's their "official" place,
# for Five 1.3 forward-compatibility.

from Products.Five.event import ObjectManagerSublocations
from Products.Five.event import dispatchObjectWillBeMovedEvent
from Products.Five.event import dispatchObjectMovedEvent
from Products.Five.event import dispatchFiveObjectClonedEvent

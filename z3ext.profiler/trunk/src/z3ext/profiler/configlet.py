##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
from zope.app.component.hooks import getSite
from zope.traversing.interfaces import IContainmentRoot


class ProfilerConfiglet(object):

    def isAvailable(self):
        if not IContainmentRoot.providedBy(getSite()):
            return False

        return super(ProfilerConfiglet, self).isAvailable()

##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Infos about utilities.
"""
import zope.component
from zope.component import globalregistry

class UtilityInfo(object):

    def __init__(self, obj=None):
        self.context = obj

    def getAllUtilities(self):
        smlist = [zope.component.getSiteManager(self.context)]
        seen = []
        result = []
        while smlist:
            sm = smlist.pop()
            if sm in seen:
                continue
            seen.append(sm)
            smlist += list(sm.__bases__)
            for u in sm.registeredUtilities():
                result.append(
                    dict(name = u.name, provided=u.provided,
                         registry=u.registry, component=u.component))
        return result

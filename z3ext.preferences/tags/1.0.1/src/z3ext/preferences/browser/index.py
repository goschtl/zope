##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
from zope.interface import Interface
from zope.component import getUtility
from zope.security import checkPermission
from z3ext.preferences.interfaces import IPreferenceGroup, IPreferenceCategory


class PreferencesView(object):

    def groups(self):
        root = self.context
        request = self.request

        groups = []
        for name, group in root.items():
            if not group.isAvailable():
                continue

            if IPreferenceCategory.providedBy(group):
                subgroups = [(sgroup.__title__,
                              sgroup.__id__.split('.')[-1], sgroup)
                             for t, sgroup in group.items() 
                             if sgroup.isAvailable()]
                if subgroups:
                    groups.append((group.__title__, group,
                                   [{'id': id, 'group': sgroup}
                                    for t, id, sgroup in subgroups]))
            else:
                groups.append((group.__title__, group, ()))

        return [{'group':group, 'subgroups': groups}
                for t, group, groups in groups]

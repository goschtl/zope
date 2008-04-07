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
""" Root Preference Group

$Id$
"""
from zope import interface
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.app.security.interfaces import IUnauthenticatedPrincipal

from i18n import _
from preference import PreferenceGroup
from interfaces import IRootPreferences, IPreferenceCategory


class PersonalPreferences(PreferenceGroup):
    interface.implements(IRootPreferences, IPreferenceCategory)

    __id__ = ''
    __name__ = u'preferences'
    __title__ = _(u'Personal preferences')
    __description__ = _('This area allows you to change personal preferences.')
    __schema__ = IRootPreferences
    __principal__ = None

    def __init__(self):
        self.__subgroups__ = ()

    def isAvailable(self):
        if IUnauthenticatedPrincipal.providedBy(self.__principal__):
            return False
        return True

    def __bind__(self, parent=None, principal=None):
        clone = super(PersonalPreferences, self).__bind__(parent, principal)

        rmanager = IPrincipalRoleManager(clone, None)
        if rmanager is not None:
            rmanager.assignRoleToPrincipal(
                'preference.Owner', clone.__principal__.id)

        return clone

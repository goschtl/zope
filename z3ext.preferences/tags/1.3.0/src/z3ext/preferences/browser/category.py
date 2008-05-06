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
""" IPreferenceCategory view

$Id$
"""
from zope import schema, interface
from zope.component import getMultiAdapter

from group import PreferenceGroup


class PreferenceCategory(PreferenceGroup):

    label = u''
    description = u''

    def update(self):
        super(PreferenceCategory, self).update()

        context = self.context
        request = self.request

        subgroups = []

        for name, group in context.items():
            if not group.isAvailable():
                continue

            view = getMultiAdapter((group, request), name='view.html')
            view.update()

            subgroups.append(view)

        self.groups = subgroups

    def renderForm(self):
        if bool(schema.getFields(self.context.__schema__)):
            return super(PreferenceCategory, self).render()
        else:
            return u''

    def render(self):
        return self.template()

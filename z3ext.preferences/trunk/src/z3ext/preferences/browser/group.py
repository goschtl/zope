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
""" IPreferenceGroup view

$Id$
"""
from zope import schema
from zope.component import getMultiAdapter
from zope.cachedescriptors.property import Lazy
from z3ext.layoutform import Fields, PageletEditForm


class PreferenceGroup(PageletEditForm):

    @property
    def prefix(self):
        return str(self.context.__id__)

    @property
    def label(self):
        return self.context.__title__

    @property
    def description(self):
        return self.context.__description__

    @Lazy
    def fields(self):
        return Fields(self.context.__schema__, omitReadOnly=True)

    def update(self):
        super(PreferenceGroup, self).update()

        context = self.context
        request = self.request

        subgroups = []

        for name, group in context.items():
            if not group.isAvailable():
                continue

            view = getMultiAdapter((group, request), name='index.html')
            view.update()

            subgroups.append(view)

        self.groups = subgroups

    def render(self):
        result = []
        
        if bool(schema.getFields(self.context.__schema__)):
            result.append(super(PreferenceGroup, self).render())

        result.extend([group.render() for group in self.groups])

        return u'<br />\n'.join(result)

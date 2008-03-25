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
from zope import event, schema, interface
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.cachedescriptors.property import Lazy
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.pagetemplate.interfaces import IPageTemplate

from z3ext.layoutform import Fields, PageletEditForm
from z3ext.preferences.interfaces import IPreferenceCategory

from interfaces import IPreferenceGroupView


class PreferenceGroup(PageletEditForm):

    edit = None
    editable = False

    group = ViewPageTemplateFile('group.pt')
    template = ViewPageTemplateFile('edit.pt')

    @property
    def label(self):
        return self.context.__title__

    @property
    def description(self):
        return self.context.__description__

    @Lazy
    def fields(self):
        return Fields(self.context.__schema__)

    def update(self):
        context = self.context
        request = self.request

        if IPreferenceCategory.providedBy(context):
            subgroups = []

            for name, group in context.items():
                if not group.isAvailable():
                    continue

                view = queryMultiAdapter((group, request), IPreferenceGroupView)
                subgroups.append((group.__title__, group, view))

            self.subgroups = [{'group': group, 'view': view}
                              for t, group, view in subgroups]
        else:
            subgroups = []
            for name, group in context.items():
                if not group.isAvailable():
                    continue

                view = queryMultiAdapter((group, request), name='index.html')
                if not view:
                    continue

                view.update()
                subgroups.append((group.__title__, group, view))

            self.subgroups = [{'group': group, 'view': view}
                              for t, group, view in subgroups]

            if subgroups:
                self.editable = True

        self.hasFields = bool(schema.getFields(context.__schema__))
        if self.hasFields:
            super(PreferenceGroup, self).update()

    form_result = u''

    def render(self, subform=False):
        self.subform = subform

        if self.hasFields:
            self.editable = True
            if self.template is None:
                template = getMultiAdapter(
                    (self, self.request), IPageTemplate)
                self.form_result = template(self)
            else:
                self.form_result = self.template()

        return self.group()

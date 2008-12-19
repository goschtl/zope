##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Support for Layout Templates

$Id$
"""
from zope import interface
from zope.component import getAdapters
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.pagetemplate.interfaces import IPageTemplate

from z3c.form import form
from z3c.form.interfaces import IForm, IGroup, ISubForm

from z3ext.layout.interfaces import IPagelet
from z3ext.layout.pagelet import BrowserPagelet

from interfaces import IPageletForm, IPageletSubform
from interfaces import IPageletDisplayForm, IPageletFormView


class PageletBaseForm(form.BaseForm, BrowserPagelet):

    __call__ = BrowserPagelet.__call__

    def render(self):
        # render content template 
        if self.template is None:
            view = queryMultiAdapter((self, self.request), IPageletFormView)
            if view is not None:
                view.update()
                return view.render()

            template = getMultiAdapter((self, self.request), IPageTemplate)
            return template(self)

        return self.template()


class PageletForm(form.Form, PageletBaseForm):
    interface.implements(IPageletForm)

    label = u''
    description = u''

    forms = ()
    groups = ()
    subforms = ()

    render = PageletBaseForm.render
    __call__ = PageletBaseForm.__call__

    def extractData(self):
        data, errors = super(PageletForm, self).extractData()
        for form in self.groups:
            if not IForm.providedBy(form):
                continue

            formData, formErrors = form.extractData()
            data.update(formData)
            if formErrors:
                if errors:
                    errors += formErrors
                else:
                    errors = formErrors

        for form in self.subforms:
            if not IForm.providedBy(form):
                continue

            formData, formErrors = form.extractData()
            if formErrors:
                if errors:
                    errors += formErrors
                else:
                    errors = formErrors

        return data, errors

    def _loadSubforms(self):
        return [form for name, form in 
                getAdapters((self.context, self.request, self), IPageletSubform)]

    def updateForms(self):
        forms = []
        groups = []
        subforms = []
        for form in self._loadSubforms():
            form.update()
            if not form.isAvailable():
                continue

            if IGroup.providedBy(form):
                groups.append((form.weight, form.__name__, form))
            elif ISubForm.providedBy(form):
                subforms.append((form.weight, form.__name__, form))
            else:
                forms.append((form.weight, form.__name__, form))

        groups.sort()
        self.groups = [form for weight, name, form in groups]

        subforms.sort()
        self.subforms = [form for weight, name, form in subforms]

        forms.sort()
        self.forms = [form for weight, name, form in forms]

    def update(self):
        self.updateWidgets()
        self.updateActions()
        self.updateForms()

        if not IPageletSubform.providedBy(self):
            self.actions.execute()

        for form in self.subforms:
            form.postUpdate()
        for form in self.forms:
            form.postUpdate()

    def isAvailable(self):
        return True

    def postUpdate(self):
        self.actions.execute()


class PageletDisplayForm(PageletForm, form.DisplayForm):
    interface.implements(IPageletDisplayForm)

    render = PageletForm.render
    __call__ = PageletForm.__call__

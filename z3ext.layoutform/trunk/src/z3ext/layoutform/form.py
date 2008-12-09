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
from z3c.form.interfaces import IGroup

from z3ext.layout.interfaces import IPagelet
from z3ext.layout.pagelet import BrowserPagelet

from interfaces import IPageletForm, IPageletSubform
from interfaces import IPageletDisplayForm, IPageletFormView


class PageletForm(form.Form, BrowserPagelet):
    interface.implements(IPageletForm)

    forms = ()

    __call__ = BrowserPagelet.__call__

    def extractData(self):
        data, errors = super(PageletForm, self).extractData()
        for form in self.forms:
            if IGroup.providedBy(form):
                formData, formErrors = form.extractData()
                data.update(formData)
                if formErrors:
                    if errors:
                        errors += formErrors
                    else:
                        errors = formErrors
        return data, errors

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

    def updateForms(self):
        forms = []
        for name, form in getAdapters(
            (self.context, self.request, self), IPageletSubform):
            form.update()
            forms.append((form.weight, name, form))

        forms.sort()
        self.forms = [form for weight, name, form in forms]

    def update(self):
        self.updateWidgets()
        self.updateActions()
        self.updateForms()
        self.actions.execute()


class PageletDisplayForm(form.DisplayForm, PageletForm):
    interface.implements(IPageletDisplayForm)

    render = PageletForm.render
    __call__ = PageletForm.__call__

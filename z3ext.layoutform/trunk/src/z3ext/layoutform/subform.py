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
""" 

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
from zope import interface, event
from zope.component import queryMultiAdapter
from zope.traversing.browser import absoluteURL
from zope.lifecycleevent import ObjectModifiedEvent

from z3c.form import subform, button
from z3c.form.interfaces import ISubForm, IActionHandler
from z3ext.statusmessage.interfaces import IStatusMessage

from utils import applyChanges
from form import PageletBaseForm
from interfaces import _, IPageletEditSubForm, IPageletSubform, ISaveButton


class PageletEditSubForm(subform.EditSubForm, PageletBaseForm):
    interface.implements(IPageletEditSubForm)

    label = u''
    description = u''

    render = PageletBaseForm.render
    __call__ = PageletBaseForm.__call__

    @button.handler(ISaveButton)
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            IStatusMessage(self.request).add(
                (self.formErrorsMessage,) + errors, 'formError')
        else:
            content = self.getContent()
            changed = applyChanges(self, content, data)
            if changed:
                event.notify(ObjectModifiedEvent(content))

    def executeActions(self, form):
        request = self.request
        content = self.getContent()

        if hasattr(form, 'actions'):
            for action in form.actions.executedActions:
                adapter = queryMultiAdapter(
                    (self, request, content, action), IActionHandler)
                if adapter:
                    adapter()

        if ISubForm.providedBy(form):
            self.executeActions(form.parentForm)
        elif IPageletSubform.providedBy(form) and form.managers:
            self.executeActions(form.managers[0])

    def update(self):
        self.updateWidgets()

        if not IPageletSubform.providedBy(self):
            self.executeActions(self.parentForm)

    def isAvailable(self):
        return True

    def postUpdate(self):
        self.executeActions(self.parentForm)

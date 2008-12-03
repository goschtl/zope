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
from zope.traversing.browser import absoluteURL
from zope.lifecycleevent import ObjectModifiedEvent

from z3c.form import form, subform, button
from z3ext.statusmessage.interfaces import IStatusMessage

from form import PageletForm
from interfaces import _, IPageletEditSubForm, ISaveButton


class PageletEditSubForm(subform.EditSubForm, PageletForm):
    interface.implements(IPageletEditSubForm)

    render = PageletForm.render
    __call__ = PageletForm.__call__

    @button.buttonAndHandler(
        _(u'Save'), name='save', provides=ISaveButton)
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            IStatusMessage(self.request).add(
                (self.formErrorsMessage,) + errors, 'formError')
        else:
            content = self.getContent()
            changed = form.applyChanges(self, content, data)
            if changed:
                event.notify(ObjectModifiedEvent(content))
                IStatusMessage(self.request).add(self.successMessage)
            else:
                IStatusMessage(self.request).add(self.noChangesMessage)

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
from zope import interface, event
from zope.lifecycleevent import ObjectCreatedEvent
from zope.traversing.browser import absoluteURL
from zope.app.container.interfaces import IAdding
from zope.app.container.interfaces import IWriteContainer
from zope.app.container.interfaces import IContainerNamesContainer

from z3c.form import form, button
from z3ext.layout.pagelet import BrowserPagelet
from z3ext.statusmessage.interfaces import IStatusMessage

import interfaces
from interfaces import _


class PageletAddForm(form.AddForm, BrowserPagelet):
    interface.implements(interfaces.IPageletAddForm)

    render = BrowserPagelet.render
    __call__ = BrowserPagelet.__call__

    _addedObject = None

    formCancelMessage = _(u'Action has been canceled.')

    @button.buttonAndHandler(_(u'Add'), name='add',
                             provides=interfaces.IAddButton)
    def handleAdd(self, action):
        data, errors = self.extractData()

        if errors:
            IStatusMessage(self.request).add(self.formErrorsMessage, 'warning')
        else:
            obj = self.createAndAdd(data)

            if obj is not None:
                self._addedObject = obj
                self._finishedAdd = True
                self.redirect(self.nextURL())

    @button.buttonAndHandler(_(u'Cancel'), name='cancel',
                             provides=interfaces.ICancelButton)
    def handleCancel(self, action):
        self._finishedAdd = True
        self.redirect(self.cancelURL())
        IStatusMessage(self.request).add(self.formCancelMessage)

    def createAndAdd(self, data):
        obj = self.create(data)
        event.notify(ObjectCreatedEvent(obj))
        self.add(obj)
        return obj

    def nextURL(self):
        if self._addedObject is None:
            return '%s/@@SelectedManagementView.html'%\
                   absoluteURL(self.context, self.request)
        else:
            return absoluteURL(self._addedObject, self.request) + '/'

    def cancelURL(self):
        context = self.context

        if IAdding.providedBy(context):
            return '%s/'%absoluteURL(context.context, self.request)
        else:
            return '%s/'%absoluteURL(context, self.request)

    def nameAllowed(self):
        """Return whether names can be input by the user."""
        context = self.context

        if IAdding.providedBy(context):
            context = context.context

        if IWriteContainer.providedBy(context):
            return not IContainerNamesContainer.providedBy(context)
        else:
            return False

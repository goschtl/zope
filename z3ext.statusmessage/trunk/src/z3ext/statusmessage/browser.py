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
from zope import interface, component
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider

import interfaces
from interfaces import IMessageView, IStatusMessage


class StatusMessage(object):
    interface.implements(IContentProvider)
    component.adapts(
        interface.Interface,
        interface.Interface,
        interface.Interface)

    def __init__(self, context, request, view):
        self.context, self.request, self.view = context, request, view

    def add(self, text, type='info'):
        service = IStatusMessage(self.request, None)
        if service is not None:
            service.add(text, type)

    def addIf(self, text, type='info'):
        if bool(text):
            self.add(text, type)

    def update(self):
        pass

    def render(self):
        request = self.request

        service = IStatusMessage(self.request, None)
        if service is not None:
            try:
                messages = service.clear()
            except:
                return u''
            
            views = []
            for message in messages:
                view = getMultiAdapter((message, request), IMessageView)
                views.append(view.render())

            return u'\n'.join(views)

        return u''



class BaseView(object):
    interface.implements(IMessageView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def render(self):
        return self.template%self.context.message


class Message(BaseView):
    component.adapts(
        interfaces.IMessage,
        interface.Interface)

    template = '<div class="statusMessage">%s</div>'
    

class InformationMessage(BaseView):
    component.adapts(
        interfaces.IInformationMessage,
        interface.Interface)

    template = '<div class="statusMessage">%s</div>'


class ErrorMessage(BaseView):
    component.adapts(
        interfaces.IErrorMessage,
        interface.Interface)

    template = '<div class="statusStopMessage">%s</div>'


class WarningMessage(BaseView):
    component.adapts(
        interfaces.IWarningMessage,
        interface.Interface)

    template = '<div class="statusWarningMessage">%s</div>'

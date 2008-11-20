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
import cgi
from zope import interface, component
from zope.contentprovider.interfaces import IContentProvider
from zope.publisher.interfaces.browser import IBrowserRequest

from interfaces import IMessage


class Message(object):
    interface.implements(IMessage)
    component.adapts(IBrowserRequest)

    def __init__(self, request):
        self.request = request


class InformationMessage(Message):

    def render(self, message):
        return '<div class="statusMessage">%s</div>'%message


class WarningMessage(Message):

    def render(self, message):
        return '<div class="statusWarningMessage">%s</div>'%message


class ErrorMessage(Message):

    def render(self, e):
        if isinstance(e, Exception):
            message = '%s: %s'%(e.__class__.__name__, cgi.escape(str(e), True))
        else:
            message = e

        return '<div class="statusStopMessage">%s</div>'%message


class StatusMessage(object):
    interface.implements(IContentProvider)
    component.adapts(
        interface.Interface, IBrowserRequest, interface.Interface)

    def __init__(self, context, request, view):
        self.context, self.request, self.view = context, request, view

    def update(self):
        pass

    def render(self):
        return u'<!--z3ext-statusmessage-->'

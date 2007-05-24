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
"""
$Id: layer.py 197 2007-04-13 05:03:32Z rineichen $
"""

import zope.interface
import zope.component
from zope.viewlet import viewlet

from z3c.form.interfaces import IValue
from z3c.form.interfaces import IErrorViewSnippet
from z3c.form.error import ErrorViewSnippet
from z3c.form.i18n import MessageFactory as _

from zif.jsonserver.interfaces import IJSONRPCRequest


JSONFormValidateJavaScriptViewlet = viewlet.JavaScriptViewlet(
    'jsonform.validate.js')

JSONFormValidateCSSViewlet = viewlet.CSSViewlet(
    'jsonform.validate.css')


class JSONErrorViewSnippet(object):
    """Error view snippet."""
    zope.component.adapts(zope.schema.ValidationError, None, IJSONRPCRequest, 
        None, None, None)
    zope.interface.implements(IErrorViewSnippet)

    def __init__(self, error, request, widget, field, form, content):
        self.error = self.context = error
        self.request = request
        self.widget = widget
        self.field = field
        self.form = form
        self.content = content

    def update(self):
        value = zope.component.queryMultiAdapter(
            (self.context, self.request, self.widget,
             self.field, self.form, self),
            IValue, name='message')
        if value is not None:
            self.message = value.get()
        else:
            self.message = self.error.doc()

    def render(self):
        return self.message

    def __repr__(self):
        return '<%s for %s>' %(
            self.__class__.__name__, self.error.__class__.__name__)


class JSONValueErrorViewSnippet(JSONErrorViewSnippet):
    """An error view for ValueError."""
    zope.component.adapts(ValueError, None, IJSONRPCRequest, None, None, None)

    message = _('The system could not process the given value.')

    def update(self):
        value = zope.component.queryMultiAdapter(
            (self.context, self.request, self.widget,
             self.field, self.form, self),
            IValue, name='message')
        if value is not None:
            self.message = value.get()

    def render(self):
        return self.message
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
"""Javascript-based Value Validator

$Id: $
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.component
from zope.publisher.interfaces import NotFound

from z3c.form.interfaces import IWidget, IField

from z3c.formjs import ajax, interfaces

class BaseValidator(ajax.AJAXRequestHandler):
    zope.interface.implements(interfaces.IAJAXValidator)

    # See ``interfaces.IAJAXValidator``
    ValidationScript = None

    def _validate(self):
        shortName = self.request.get('widget-name')
        self.fields = self.fields.select(shortName)
        self.updateWidgets()
        return self.widgets.extract()


class MessageValidationScript(object):
    zope.interface.implements(interfaces.IMessageValidationScript)

    def __init__(self, form, widget):
        self.form = form
        self.widget = widget

    def render(self):
        renderer = zope.component.getMultiAdapter(
            (self, self.form.request), interfaces.IRenderer)
        return renderer.render()

class MessageValidator(BaseValidator):
    '''Validator that sends error messages for widget in questiodn.'''
    ValidationScript = MessageValidationScript

    @ajax.handler
    def validate(self):
        data, errors = self._validate()
        if errors:
            return unicode(errors[0].message)
        return u'' # all OK

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

from z3c.traverser.traverser import SingleAttributeTraverserPlugin
from z3c.traverser.interfaces import IPluggableTraverser, ITraverserPlugin
from z3c.form.interfaces import IWidget, IField

from z3c.formjs import interfaces

# Traverser Plugin to the ``validate()`` method of the ``IAJAXValidator``
ValidateTraverser = SingleAttributeTraverserPlugin('validate')

class BaseValidator(object):
    zope.interface.implements(interfaces.IAJAXValidator, IPluggableTraverser)

    # See ``interfaces.IAJAXValidator``
    ValidationScript = None

    def _validate(self):
        shortName = self.request.get('widget-name')
        self.fields = self.fields.select(shortName)
        self.updateWidgets()
        return self.widgets.extract()

    def publishTraverse(self, request, name):
        # Act like a pluggable traverser.
        for traverser in zope.component.subscribers(
                 (self, request), ITraverserPlugin):
            try:
                return traverser.publishTraverse(request, name)
            except NotFound:
                pass


class MessageValidationScript(object):
    zope.interface.implements(interfaces.IMessageValidationScript)

    def __init__(self, form, widget):
        self.form = form
        self.widget = widget

    def render(self):
        renderer = zope.component.queryMultiAdapter(
            (self, self.form.request), interfaces.IRenderer)
        return renderer.render()

class MessageValidator(BaseValidator):
    '''Validator that sends error messages for widget in questiodn.'''
    ValidationScript = MessageValidationScript

    def validate(self):
        data, errors = self._validate()
        if errors:
            return errors[0].message
        return u'' # all OK


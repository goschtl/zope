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
"""Javascript Form Framework Interfaces.

$Id: $
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.component

from z3c.traverser.traverser import SingleAttributeTraverserPlugin
from z3c.traverser.interfaces import IPluggableTraverser, ITraverserPlugin
from z3c.form.interfaces import IWidget, IField

from z3c.formjs import interfaces


class MessageValidationRenderer(object):
    """An intermediate class that performs adapter look ups.

    This way you don't have to do as many adapter look ups in your Form class.
    """

    def __init__(self, form, field):
        self.form = form
        self.field = field

    def render(self):
        jsrenderer = zope.component.queryMultiAdapter(
            (self.form, self.field, self.form.request),
            interfaces.IJSMessageValidationRenderer)
        return jsrenderer.render()


class BaseValidator(object):
    zope.interface.implements(interfaces.IAJAXValidator,
                              IPluggableTraverser)

    ValidationRenderer = None

    def _validate(self):
        # XXX: Hard coded. Need a better approach.
        widgetID = self.request.get('widget-id')
        fieldName = widgetID.replace('form-widgets-','')
        self.fields = self.fields.select(fieldName)
        self.updateWidgets()
        return self.widgets.extract()

    def publishTraverse(self, request, name):
        # 1. Look at all the traverser plugins, whether they have an answer.
        for traverser in zope.component.subscribers((self, request),
                                                    ITraverserPlugin):
            try:
                return traverser.publishTraverse(request, name)
            except NotFound:
                pass


class MessageValidator(BaseValidator):
    '''Validator that sends error messages for widget in questiodn.'''
    ValidationRenderer = MessageValidationRenderer

    def validate(self):
        data, errors = self._validate()
        if errors:
            return errors[0].message
        return u'' # all OK

ValidateTraverser = SingleAttributeTraverserPlugin('validate')

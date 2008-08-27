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
"""Validator Form

$Id$
"""
__docformat__="restructuredtext"
import os.path
import zope.interface
import zope.schema
from zope.viewlet.viewlet import CSSViewlet, JavaScriptViewlet
from z3c.form import form, button, field
from z3c.form.interfaces import IWidgets
from z3c.formui import layout
from z3c.formjs import jsaction, jsevent, jsvalidator, interfaces

ValidatorJSViewlet = JavaScriptViewlet('validator.js')
ValidatorCSSViewlet = CSSViewlet('validator.css')

class IFields(zope.interface.Interface):
    int = zope.schema.Int(
        title=u"Integer",
        description=u"Enter an Integer",
        required=True)

    float = zope.schema.Float(
        title=u"Float",
        description=u"Enter a Float",
        required=True)

    textLine = zope.schema.TextLine(
        title=u"Text Line",
        description=u"Enter any Text",
        required=True)

    asciiLine = zope.schema.ASCIILine(
        title=u"ASCII Line",
        description=u"Enter any ASCII",
        required=True)

    URI = zope.schema.URI(
        title=u"URI",
        description=u"Enter a URL",
        required=True)


class ValidatorForm(
    layout.FormLayoutSupport, jsvalidator.MessageValidator, form.Form):

    fields = field.Fields(IFields)
    label = u'JavaScript AJAX Validation'

    @jsaction.handler(zope.schema.interfaces.IField, event=jsevent.CHANGE)
    def fieldValidator(self, event, selector):
        return self.ValidationScript(self, selector.widget).render()

    def updateWidgets(self):
        '''See interfaces.IForm'''
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.ignoreContext = True
        self.widgets.update()

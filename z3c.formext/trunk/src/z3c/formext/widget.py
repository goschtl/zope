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
"""ExtJS Widgets.

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema.interfaces
import zope.component

from z3c.form.browser.checkbox import SingleCheckBoxWidget
from z3c.form.browser.text import TextWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import ITextWidget
from z3c.form.interfaces import NOVALUE
from z3c.form.widget import FieldWidget, Widget

from z3c.formext import interfaces

class ExtJSDateWidget(TextWidget):
    zope.interface.implementsOnly(interfaces.IExtJSDateWidget)

@zope.component.adapter(zope.schema.interfaces.IField, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def ExtJSDateFieldWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return FieldWidget(field, ExtJSDateWidget(request))



class ExtJSSingleCheckBoxWidget(SingleCheckBoxWidget):
    zope.interface.implementsOnly(interfaces.IExtJSSingleCheckBoxWidget)

    def extract(self, default=u'off'):
        return Widget.extract(self, default=default)


@zope.component.adapter(zope.schema.interfaces.IField, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def ExtJSSingleCheckBoxFieldWidget(field, request):
    """IFieldWidget factory for TextWidget."""
    return FieldWidget(field, ExtJSSingleCheckBoxWidget(request))

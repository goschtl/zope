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
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
from zope.app.form.browser.widget import renderElement
from zope.app.form.browser import TextAreaWidget
from zope.viewlet.viewlet import CSSViewlet
from zope.viewlet.viewlet import JavaScriptViewlet

from z3c.form import widget
from z3c.form.browser import textarea

from jquery.widget.resteditor import interfaces


JQueryRestEditorCSS = CSSViewlet('jquery.resteditor.css')
JQueryRestEditorJavaScript = JavaScriptViewlet('jquery.resteditor.js')


class RESTEditorWidget(textarea.TextAreaWidget):
    """Textarea widget implementation."""

    zope.interface.implementsOnly(interfaces.IRESTEditorWidget)

    css = u'restEditorWidget'
    value = u''

    # optional html attributes
    readonly = None
    accesskey = None


def RESTEditorFieldWidget(field, request):
    """IFieldWidget factory for RESTEditorWidget."""
    return widget.FieldWidget(field, RESTEditorWidget(request))

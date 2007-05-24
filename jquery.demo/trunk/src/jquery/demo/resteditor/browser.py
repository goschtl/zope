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
from zope.viewlet.viewlet import CSSViewlet
from z3c.website.browser.page import PageAddForm
from z3c.form.interfaces import IWidgets
from z3c.form import form, field
from z3c.pagelet import browser
from z3c.template.interfaces import ILayoutTemplate

from z3c.website.interfaces import IContent
from z3c.website.interfaces import ISessionData
from z3c.website.browser.sample import SampleAddForm
from z3c.website.browser.sample import SessionDataEditForm
from jquery.demo.i18n import MessageFactory as _
from jquery.widget.resteditor.browser import RESTEditorFieldWidget
from jquery.demo.resteditor import app


class AddForm(SampleAddForm):

    label = _('Add REST Editor sample')
    factory = app.RESTEditorSample


class SamplePage(SessionDataEditForm):
    """Sample edit page"""

    name = u'RestEditorSample'

    fields = field.Fields(ISessionData).select('content')
    fields['content'].widgetFactory = RESTEditorFieldWidget


# This is the enhanced content edit form for ISample

RestEditorCSS = CSSViewlet('resteditor.css')


class ContentEditPagelet(form.EditForm):
    """Content edit page."""

    fields = field.Fields(IContent).select('body')

    fields['body'].widgetFactory = RESTEditorFieldWidget

    def __call__(self):
        self.update()
        layout = zope.component.getMultiAdapter((self, self.request),
            ILayoutTemplate)
        return layout(self)

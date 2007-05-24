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

from z3c.website.i18n import MessageFactory as _
from z3c.website.browser.page import PageAddForm
from z3c.demo.calculator import calculator

from z3c.template.interfaces import ILayoutTemplate
from z3c.form.interfaces import IWidgets
from z3c.form import form
from z3c.form import field
from z3c.website.browser.sample import SampleAddForm
from z3c.website.browser.sample import SessionDataEditForm
from jquery.demo.jsonform import interfaces
from jquery.demo.jsonform import app


class AddForm(SampleAddForm):

    label = _('Add JSON form sample')
    factory = app.JSONFormSample


class SampleForm(SessionDataEditForm):
    """Sample edit form"""

    # we apply the JQuery xpath to this form name
    id = u'JSONValidateSample'

    fields = field.Fields(interfaces.IAnotherSessionData).select('asciiField', 
        'asciiLineField', 'dateField', 'datetimeField', 'decimalField', 
        'dottedNameField', 'floatField', 'idField')

    def getContentFactory(self):
        return app.AnotherSessionData

    def publishTraverse(self, request, name):
        if name == 'jsonValidate':
            view = zope.component.queryMultiAdapter((self, request), name=name)
            if view is None:
                raise NotFound(self, name, request)
            return view
        else:
            raise NotFound(self, name, request)

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
from z3c.pagelet import browser
from z3c.website.browser.sample import SampleAddForm
from jquery.demo.livesearch import interfaces
from jquery.demo.livesearch import app


class AddForm(SampleAddForm):

    label = _('Add LiveSearch sample')
    factory = app.LiveSearchSample


class SamplePagelet(browser.BrowserPagelet):
    """Sample live search form"""

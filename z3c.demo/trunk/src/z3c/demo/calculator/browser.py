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
$Id: __init__.py 69382 2006-08-09 13:26:53Z rogerineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
from zope.component.interfaces import IFactory
from zope.dublincore.interfaces import IZopeDublinCore
from zope.traversing.browser import absoluteURL
from zope.traversing import api
from zope.app.renderer.rest import ReStructuredTextToHTMLRenderer
from zc.table import column
from zc.table import table

from z3c.configurator import configurator
from z3c.pagelet import browser
from z3c.form import form
from z3c.form import field
from z3c.form import widget
from z3c.template.interfaces import ILayoutTemplate

from z3c.website.i18n import MessageFactory as _
from z3c.website.browser.page import PageAddForm
from z3c.demo.calculator import calculator


class CalculatorAddForm(PageAddForm):

    label = _('Add Calculator sample')
    factory = calculator.Calculator

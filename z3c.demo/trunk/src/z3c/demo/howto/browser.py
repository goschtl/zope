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
from z3c.pagelet import browser
from z3c.website.browser.sample import SampleAddForm
from z3c.website.interfaces import ISamplePagelet
from z3c.demo.i18n import MessageFactory as _
from z3c.demo.howto import app


class HowToAddForm(SampleAddForm):
    """Add form for HowTo sample object."""

    label = _(u'Add HowTo sample')
    factory = app.HowToSample


class HowToSample(browser.BrowserPagelet):
    """Sample page."""

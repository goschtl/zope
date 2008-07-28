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
"""Form and Widget Framework Interfaces

$Id: interfaces.py 77536 2007-07-06 21:13:41Z srichter $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema
from zope.interface.common import mapping
from zope.location.interfaces import ILocation
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.pagetemplate.interfaces import IPageTemplate

from z3c.form.i18n import MessageFactory as _


class ISnippets(ILocation):
    """HTML snippets around a widget"""

class IErrorstatusTemplate(IPageTemplate):
    """Marker interface for Errorstatus templates"""

class IFormframeTemplate(IPageTemplate):
    """Marker interface for formframe templates"""


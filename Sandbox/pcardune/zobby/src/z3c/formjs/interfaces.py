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

$Id: interfaces.py 215 2007-05-03 19:34:42Z srichter $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema
import zope.configuration.fields
from zope.interface.common import mapping
from zope.location.interfaces import ILocation
from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.interfaces.browser import IBrowserRequest

from z3c.form.interfaces import IFormLayer
from z3c.formjs.i18n import MessageFactory as _


# ----[ Layer Declaration ]--------------------------------------------------

class IFormJSLayer(IFormLayer):
    """A layer that contains all registrations of this package.

    It is intended that someone can just use this layer as a base layer when
    using this package.
    """


class IJSForm(zope.interface.Interface):
    """Marker interface to make forms use javascript widgets."""

##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Demo widget implementation

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope.schema import Int

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.demo.widget.interfaces import IDemoWidget


class IReadDemoIntWidget(Interface):
    """Widget read interface."""

    readonly = Int(
        title = _(u"readonly"),
        description=_(u"zope.schema.Int field with readonly = True."),
        required=False,
        readonly=True,
        default=42)


class IWriteDemoIntWidget(Interface):
    """Widget write interface."""

    standard = Int(
        title = _(u"standard"),
        description=_(u"""zope.schema.Int field with only title and description."""),
        )

    required = Int(
        title = _(u"required"),
        description=_(u"zope.schema.Int field with required = True."),
        required=True)

    constraint = Int(
        title = _(u"constraint"),
        description=_(u"""zope.schema.Int field with constraint """
            """lambda x: x == 42."""),
        constraint=lambda x: x == 42)

    default = Int(
        title = _(u"default"),
        description=_(u"""zope.schema.Int field with """
            """default = u'default'."""),
        default=42)

    min = Int(
        title = _(u"min"),
        description=_(u"zope.schema.Int field with min = 5."),
        min=5)

    max = Int(
        title = _(u"max"),
        description=_(u"zope.schema.Int field with max = 10"),
        max=10)

    min_max = Int(
        title = _(u"min_max"),
        description=_(u"""zope.schema.Int field with min = 5 and max = 10"""),
        min=5,
        max=10)


class IDemoIntWidget(IDemoWidget, IReadDemoIntWidget, IWriteDemoIntWidget):
    """Widget interface inherits read and write interfaces."""

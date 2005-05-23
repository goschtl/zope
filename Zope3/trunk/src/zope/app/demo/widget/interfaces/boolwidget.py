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
from zope.schema import Bool

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.demo.widget.interfaces import IDemoWidget


class IReadDemoBoolWidget(Interface):
    """Widget read interface."""

    readonly = Bool(
        title = _(u"readonly"),
        description=_(u"zope.schema.Int field with readonly = True."),
        required=False,
        readonly=True,
        default=42)


class IWriteDemoBoolWidget(Interface):
    """Widget write interface."""

    standard = Bool(
        title = _(u"standard"),
        description=_(u"""zope.schema.Bool field with only title and description."""),
        )

    required = Bool(
        title = _(u"required"),
        description=_(u"zope.schema.Bool field with required = True."),
        required=True)

    constraint = Bool(
        title = _(u"constraint"),
        description=_(u"""zope.schema.Bool field with constraint """
            """lambda x: x == True."""),
        constraint=lambda x: x == True)

    default = Bool(
        title = _(u"default"),
        description=_(u"""zope.schema.Bool field with """
            """default = True."""),
        default=True)


class IDemoBoolWidget(IDemoWidget, IReadDemoBoolWidget, IWriteDemoBoolWidget):
    """Widget interface inherits read and write interfaces."""

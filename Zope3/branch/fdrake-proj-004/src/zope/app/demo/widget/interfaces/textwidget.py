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
from zope.schema import TextLine

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.demo.widget.interfaces import IDemoWidget


class IReadDemoTextWidget(Interface):
    """Widget read interface."""

    readonly = TextLine(
        title = _(u"readonly"),
        description=_(u"zope.schema.TextLine field with readonly = True."),
        required=False,
        readonly=True,
        default=u'readonly')


class IWriteDemoTextWidget(Interface):
    """Widget write interface."""

    standard = TextLine(
        title = _(u"standard"),
        description=_(u"""zope.schema.TextLine field with only title and description."""),
        )

    required = TextLine(
        title = _(u"required"),
        description=_(u"zope.schema.TextLine field with required = True."),
        required=True)

    constraint = TextLine(
        title = _(u"constraint"),
        description=_(u"""zope.schema.TextLine field with """
            """constraint = lambda x: x == u'constraint'."""),
        constraint=lambda x: x == u'constraint')

    default = TextLine(
        title = _(u"default"),
        description=_(u"""zope.schema.TextLine field with """
            """default = u'default'."""),
        default=u'default')

    min_length = TextLine(
        title = _(u"min_length"),
        description=_(u"zope.schema.TextLine field with min_length = 5."),
        min_length=5)

    max_length = TextLine(
        title = _(u"max_length"),
        description=_(u"zope.schema.TextLine field with max_length = 10"),
        max_length=10)

    min_max = TextLine(
        title = _(u"min_max"),
        description=_(u"""zope.schema.TextLine field with min_lenght = 5 """
            """and max_length = 10"""),
        min_length=5,
        max_length=10)


class IDemoTextWidget(IDemoWidget, IReadDemoTextWidget, IWriteDemoTextWidget):
    """Widget interface inherites read and write interfaces."""

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
from zope.schema import Text

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.demo.widget.interfaces import IDemoWidget


class IReadDemoTextAreaWidget(Interface):
    """Widget read interface."""

    readonly = Text(
        title = _(u"readonly"),
        description=_(u"zope.schema.Text field with readonly = True."),
        required=False,
        readonly=True,
        default=u'readonly')

class IWriteDemoTextAreaWidget(Interface):
    """Widget write interface."""

    standard = Text(
        title = _(u"standard"),
        description=_(u"""zope.schema.Text field with only title and description."""),
        )

    required = Text(
        title = _(u"required"),
        description=_(u"zope.schema.Text field with required = True."),
        required=True)

    constraint = Text(
        title = _(u"constraint"),
        description=_(u"""zope.schema.Text field with """
            """constraint = lambda x: x == u'constraint'."""),
        constraint=lambda x: x == u'constraint')

    default = Text(
        title = _(u"default"),
        description=_(u"""zope.schema.Text field with """
            """default = u'default'."""),
        default=u'default')

    min_length = Text(
        title = _(u"min_length"),
        description=_(u"zope.schema.Text field with min_length = 5."),
        min_length=5)

    max_length = Text(
        title = _(u"max_length"),
        description=_(u"zope.schema.Text field with max_length = 10"),
        max_length=10)

    min_max = Text(
        title = _(u"min_max"),
        description=_(u"""zope.schema.Text field with min_lenght = 5 """
            """and max_length = 10"""),
        min_length=5,
        max_length=10)


class IDemoTextAreaWidget(IDemoWidget, IReadDemoTextAreaWidget, 
    IWriteDemoTextAreaWidget):
    """Widget interface inherits read and write interfaces."""

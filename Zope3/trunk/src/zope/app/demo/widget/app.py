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

from persistent import Persistent
from zope.interface import implements

from zope.app.container.contained import Contained
from zope.app.container.btree import BTreeContainer

from zope.app.demo.widget.interfaces import IDemoWidgetContainerContained
from zope.app.demo.widget.interfaces import IDemoWidgetContainer
from zope.app.demo.widget.interfaces import IDemoWidget


class DemoWidgetContainer(BTreeContainer):
    """Demo widget container containing demo widget objects"""

    implements(IDemoWidgetContainer)


class DemoWidget(Persistent, Contained):
    """Base class for demo widgets."""

    implements(IDemoWidgetContainerContained)

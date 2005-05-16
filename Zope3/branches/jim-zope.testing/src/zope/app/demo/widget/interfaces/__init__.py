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
"""Interfaces for demo widget implementation

$Id$
"""
from zope.interface import Interface
from zope.schema import Field

from zope.app.container.interfaces import IContained, IContainer
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition


class IDemoWidget(Interface):
    """Base interface for demo widget."""


class IDemoWidgetContainer(IContainer):
    """Interface for the demo widgets container.
    
    We use a precondition for to let just childs to be added which implements
    the interface ITiksSampleContent
    """

    def __setitem__(name, object):
        """Add a widget demo content"""

    __setitem__.precondition = ItemTypePrecondition(IDemoWidget)


class IDemoWidgetContainerContained(IContained):
    """Constraint interface for let object contained in IDemoWidgetContainer.

    """

    __parent__ = Field(
             constraint = ContainerTypesConstraint(IDemoWidgetContainer))


from zope.app.demo.widget.interfaces.boolwidget import IReadDemoBoolWidget
from zope.app.demo.widget.interfaces.boolwidget import IWriteDemoBoolWidget
from zope.app.demo.widget.interfaces.boolwidget import IDemoBoolWidget

from zope.app.demo.widget.interfaces.intwidget import IReadDemoIntWidget
from zope.app.demo.widget.interfaces.intwidget import IWriteDemoIntWidget
from zope.app.demo.widget.interfaces.intwidget import IDemoIntWidget

from zope.app.demo.widget.interfaces.textareawidget import IReadDemoTextAreaWidget
from zope.app.demo.widget.interfaces.textareawidget import IWriteDemoTextAreaWidget
from zope.app.demo.widget.interfaces.textareawidget import IDemoTextAreaWidget

from zope.app.demo.widget.interfaces.textwidget import IReadDemoTextWidget
from zope.app.demo.widget.interfaces.textwidget import IWriteDemoTextWidget
from zope.app.demo.widget.interfaces.textwidget import IDemoTextWidget

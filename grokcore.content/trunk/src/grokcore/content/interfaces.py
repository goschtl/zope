# -*- coding: utf-8 -*-

from grokcore.component.interfaces import IContext
from zope.container.interfaces import IOrderedContainer
from zope.container.interfaces import IContainer as IContainerBase


class IContainer(IContext, IContainerBase):
    """A Grok container.
    """

class IOrderedContainer(IContainer, IOrderedContainer):
    """A Grok container that can be ordered.
    """

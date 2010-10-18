# -*- coding: utf-8 -*-

from zope.interface import Interface


class ILayout(Interface):
    """Layout code.
    """

class IPage(Interface):
    """A template using a layout to render itself.
    """

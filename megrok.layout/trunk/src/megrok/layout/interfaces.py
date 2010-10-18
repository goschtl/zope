# -*- coding: utf-8 -*-

from grokcore.view import interfaces
from zope.interface import Interface


class ILayout(Interface):
    """Layout code.
    """


class IPageAware(Interface):
    """A view which is able to use a layout to render itself.
    """

    def contents():
        """Return the content of the page to be included in the
        layout.
        """


class IPage(IPageAware, interfaces.IGrokView):
    """A template using a layout to render itself.
    """


class ICodePage(IPage):
    """A template using a layout to render itself.
    """


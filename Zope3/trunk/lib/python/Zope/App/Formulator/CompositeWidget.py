##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""

$Id: CompositeWidget.py,v 1.2 2002/06/10 23:27:46 jim Exp $
"""

from ICompositeWidget import ICompositeWidget
from Widget import Widget


class CompositeWidget(Widget):
    """ """

    __implements__ = Widget.__implements__, ICompositeWidget

    # Page template that is ised to lay out sub-widgets
    template = None

    # List of Sub-Widgets
    widgets = None


    def render(self, REQUEST):
        """ """
        return apply(self.template, (REQUEST,))


    def render_hidden(self, REQUEST):
        """ """
        return apply(self.template, (REQUEST,), {'hidden': 1})


    def setWidget(self, name, widget):
        """ """
        if self.widgets is None:
            self.widgets = {}

        self.widgets[name] = widget


    def getWidget(self, name, _default=None):
        """ """
        if name in self.widgets.keys():
            return self.widgets[name]
        else:
            return _default


    def getWidgets(self):
        """ """
        return self.widgets

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

$Id: IBrowserWidget.py,v 1.1 2002/07/14 13:32:53 srichter Exp $
"""

from Zope.App.Forms.IWidget import IWidget


class IBrowserWidget(IWidget):
    """A field widget contains all the properties that are required
       to represent a field. Properties include css_sheet, 
       default value and so on.
    """


    def render(field, key, value):
        """Renders this widget as HTML using property values in field."""

        
    def render_hidden(field, key, value):
        """Renders this widget as a hidden field."""
        

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

$Id: IBrowserWidget.py,v 1.2 2002/06/10 23:27:49 jim Exp $
"""

from Interface import Interface


class IBrowserWidget(Interface):
    """A field widget contains all the properties that are required
       to represent a field. Properties include css_sheet, 
       default value and so on.

    """


    def render(field, key, value, REQUEST):
        """Renders this widget as HTML using property values in field.
        """

        
    def render_hidden(field, key, value, REQUEST):
        """Renders this widget as a hidden field.
        """
        

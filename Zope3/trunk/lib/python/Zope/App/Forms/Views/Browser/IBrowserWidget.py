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

$Id: IBrowserWidget.py,v 1.3 2002/10/28 23:52:31 jim Exp $
"""

from Zope.App.Forms.IWidget import IWidget


class IBrowserWidget(IWidget):
    """A field widget contains all the properties that are required
       to represent a field. Properties include css_sheet, 
       default value and so on.
    """

    def setPrefix(self, prefix):
        """Set the form-variable name prefix used for the widget

        The widget will define it's own form variable names by
        concatinating the profix and the field name using a dot. For
        example, with a prefix of "page" and a field name of "title",
        a form name of "page.title" will be used. A widget may use
        multiple form fields. If so, it should add distinguishing
        suffixes to the prefix and field name.
        """

    def __call__():
        """Render the widget
        """

    def hidden():
        """Render the widget as a hidden field
        """
    

    # XXX The following methods are being supported for backward compatability
    # They are depricated and will be refactored away eventually.

    def render(value):
        """Renders this widget as HTML using property values in field.

        The value if given will be used as the default value for the widget.  
        """
        
    def renderHidden(value):
        """Renders this widget as a hidden field.
        """
        

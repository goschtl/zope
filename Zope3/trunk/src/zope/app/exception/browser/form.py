##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Form-related exception views

$Id: form.py,v 1.1 2004/03/14 04:44:51 srichter Exp $
"""

from zope.app.form.interfaces import IWidgetInputError
from cgi import escape

class WidgetInputErrorView:
    """Displat an input error as a snippet of text"""

    __used_for__ = IWidgetInputError

    def __init__(self, context, request):
        self.context, self.request = context, request

    def snippet(self):
        """Convert a widget input error to an html snippet

        >>> from zope.app.form.interfaces import WidgetInputError
        >>> err = WidgetInputError("foo", "Foo", ["Foo input < 1"])
        >>> view = WidgetInputErrorView(err, None)
        >>> view.snippet()
        '<span class="error">Foo input &lt; 1</span>'
        """
        return '<span class="error">%s</span>' % escape(self.context.errors[0])

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
$Id: zpt.py,v 1.3 2003/03/25 20:46:13 jim Exp $
"""

import zope.schema
from zope.interface import Interface, Attribute
from zope.app.i18n import ZopeMessageIDFactory as _

class IZPTPage(Interface):
    """ZPT Pages are a persistent implementation of Page Templates.

       Note: I introduced some new methods whose functionality is
             actually already covered by some other methods but I
             want to start enforcing a common coding standard.
    """

    def setSource(text, content_type='text/html'):
        """Save the source of the page template.

        'text' must be Unicode.
        """

    def getSource():
        """Get the source of the page template."""

    source = zope.schema.Text(
        title=_(u"Source"),
        description=_(u"""The source of the page template."""),
        required=True)

    expand = zope.schema.Bool(
        title=_(u"Expand macros"),
        )

class IRenderZPTPage(Interface):

    content_type = Attribute('Content type of generated output')

    def render(request, *args, **kw):
        """Render the page template.

        The first argument is bound to the top-level 'request'
        variable. The positional arguments are bound to the 'args'
        variable and the keyword arguments are bound to the 'options'
        variable.
        """


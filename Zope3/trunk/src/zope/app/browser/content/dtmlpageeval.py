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
"""Define view component for ZPT page eval results.

$Id: dtmlpageeval.py,v 1.2 2002/12/25 14:12:30 jim Exp $
"""

from zope.publisher.browser import BrowserView
from zope.proxy.context import getWrapperContainer

class DTMLPageEval(BrowserView):

    def index(self, REQUEST=None, **kw):
        """Call a Page Template"""

        template = self.context
        return template.render(REQUEST, **kw)

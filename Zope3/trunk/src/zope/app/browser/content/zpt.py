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

$Id: zpt.py,v 1.3 2003/01/25 13:34:15 jim Exp $
"""

from zope.publisher.browser import BrowserView

class ZPTPageEval(BrowserView):

    def index(self, **kw):
        """Call a Page Template"""

        template = self.context
        request = self.request

        request.response.setHeader('content-type',
                                   template.content_type)

        return template.render(request, **kw)

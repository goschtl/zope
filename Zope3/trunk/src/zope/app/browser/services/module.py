##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Handle form to create module

$Id: module.py,v 1.2 2002/12/25 14:12:36 jim Exp $
"""

from zope.publisher.browser import BrowserView
from zope.app.services.module import Manager

class AddModule(BrowserView):

    def action(self, name, source):
        mgr = Manager()
        mgr = self.context.add(mgr)
        mgr.new(name, source)
        self.request.response.redirect(self.context.nextURL())


"""Handle form to edit module

$Id: module.py,v 1.2 2002/12/25 14:12:36 jim Exp $
"""

from zope.publisher.browser import BrowserView
from zope.app.services.module import Manager

class EditModule(BrowserView):

    def update(self):
        if "source" in self.request:
            self.context.update(self.request["source"])
            return u"The source was updated."
        else:
            return u""

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

$Id: module.py,v 1.4 2002/12/30 21:28:20 jeremy Exp $
"""

from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.services.module import Manager
from zope.component import getAdapter
from zope.publisher.browser import BrowserView

class AddModule(BrowserView):

    def action(self, name, source):
        mgr = Manager()
        mgr = self.context.add(mgr)
        mgr.new(name, source)
        # For better or worse, the name Zope uses to manage a module
        # can be different than the name Python code uses to import
        # the module.  Set the title metadata of the Zope module to
        # the real name.
        dc = getAdapter(mgr, IZopeDublinCore)
        dc.title = name
        self.request.response.redirect(self.context.nextURL())

class EditModule(BrowserView):

    def update(self):
        if "source" in self.request:
            self.context.update(self.request["source"])
            return u"The source was updated."
        else:
            return u""

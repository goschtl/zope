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

$Id: __init__.py,v 1.4 2003/08/21 21:57:41 fdrake Exp $
"""

from zope.app.services.module import Manager
from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.publisher.browser import BrowserView

from zope.app.i18n import ZopeMessageIDFactory as _


class AddModule(BrowserView):

    def action(self, source):
        name = self.context.contentName
        if not name:
            raise UserError(_(u"module name must be provided"))
        mgr = Manager(name, source)
        mgr = self.context.add(mgr)  # local registration
        mgr.execute()
        self.request.response.redirect(self.context.nextURL())
        publish(self.context.context, ObjectCreatedEvent(mgr))

class EditModule(BrowserView):

    def update(self):
        if "source" in self.request:
            self.context.source = self.request["source"]
            self.context.execute()
            return _(u"The source was updated.")
        else:
            return u""

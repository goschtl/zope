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

$Id$
"""
from zope.app.module import Manager
from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.publisher.browser import BrowserView
from zope.proxy import removeAllProxies
from zope.app.exception.interfaces import UserError

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

class ViewModule(BrowserView):

    def getModuleName(self):
        module = removeAllProxies(self.context.getModule())
        remove_keys = ['__name__', '__builtins__', '_p_serial']

        L = [(getattr(obj, '__name__', id),
              getattr(obj, '__doc__', ''),
              type(obj).__name__
              )
             for id, obj in module.__dict__.items()
             if id not in remove_keys]
        L.sort()

        l_dict = [{"name": name, "doc": doc, "objtype": objtype} for name, doc, objtype in L]

        for dic in l_dict:
                if dic['objtype'].find('Class') != -1: dic['objtype'] = 'Class'
                if dic['objtype'].find('Function') != -1: dic['objtype'] = 'Function'
        return l_dict

##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: upload.py 38895 2005-10-07 15:09:36Z dominikhuber $
"""
__docformat__ = 'restructuredtext'

import zope
from zope.app import zapi
from zope.app.file.browser.file import FileUpdateView
from zope.app.file import File
from zope.app.event import objectevent
from zope.app.container.browser.adding import Adding

from zorg.live.page.client import LivePageClient
from zorg.live.page.page import LivePage

from zorg.live.page.interfaces import ILivePageManager
from zorg.live.page.interfaces import IPersonEvent
from zorg.live.page.event import Update

from zorg.live.globals import getRequest
from zorg.live.globals import getFullName


class LiveFileAdd(LivePage, FileUpdateView) :
    """ A specialization of the traditional upload view that shows the
        progress of the upload task.
    """
    
    
    def update_object(self, data, contenttype):
        
        f = File(data, contenttype)
        zope.event.notify(objectevent.ObjectCreatedEvent(f))
        
        adding = Adding(self.context, self.request)
        adding.add(f)
        self.request.response.redirect(adding.nextURL())
        return ''

    def whoIsOnline(self) :
        """ Returns a comma seperated list of names of online users. """
        manager = zapi.getUtility(ILivePageManager)
        ids = manager.whoIsOnline(self.getLocationId())
        return ", ".join([getFullName(id) for id in ids])
   

    def notify(cls, event) :

        if IPersonEvent.providedBy(event) :
            manager = zapi.getUtility(ILivePageManager)
            repr = manager.whoIsOnline(event.where)
            update = Update(id="online", html=repr)
            cls.sendEvent(update)
                    
    notify = classmethod(notify)

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
__doc__ = """ Server Control View

$Id: ServerControlView.py,v 1.2 2002/06/10 23:27:53 jim Exp $ """

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.App.OFS.ApplicationControl.ServerControl.IServerControl \
     import IServerControl
from Zope.ComponentArchitecture import getUtility

class ServerControlView(BrowserView):
    
    def serverControl(self):
        return getUtility(self.context, IServerControl)
          # XXX what are we going to do if this fails???
    
    def action(self):
        """Do the shutdown/restart!"""
        if 'restart' in self.request:
            return self.serverControl().restart() or "You restarted the server."
        elif 'shutdown' in self.request:
            return self.serverControl().shutdown() or \
            "You shut down the server."

    index = ViewPageTemplateFile('server-control.pt')


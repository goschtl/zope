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
"""Define runtime information view component for Application Control

$Id: RuntimeInfoView.py,v 1.2 2002/06/10 23:27:54 jim Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.OFS.ApplicationControl.IRuntimeInfo import IRuntimeInfo
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.ComponentArchitecture import getAdapter

class RuntimeInfoView(BrowserView):
    
    def runtimeInfo(self):
        # XXX what are we going to do if this fails???
        runtime_info = getAdapter(self.context, IRuntimeInfo)
        formatted = {}  # contains formatted runtime information
        formatted['ZopeVersion'] = runtime_info.getZopeVersion()
        formatted['PythonVersion'] = runtime_info.getPythonVersion()
        formatted['PythonPath'] = runtime_info.getPythonPath()
        formatted['SystemPlatform'] = " ".join(runtime_info.getSystemPlatform())
        formatted['CommandLine'] = " ".join(runtime_info.getCommandLine())
        formatted['ProcessId'] = runtime_info.getProcessId()

        # make a unix "uptime" uptime format
        uptime = runtime_info.getUptime()
        days = int(uptime / (60*60*24))
        uptime = uptime - days * (60*60*24)
        
        hours = int(uptime / (60*60))
        uptime = uptime - hours * (60*60)

        minutes = int(uptime / 60)
        uptime = uptime - minutes * 60

        seconds = uptime
        formatted['Uptime'] = "%s%02d:%02d:%02d" % (
            ((days or "") and "%d days, " % days), hours, minutes, seconds)

        return formatted
        
    index = ViewPageTemplateFile('runtimeinfo.pt')

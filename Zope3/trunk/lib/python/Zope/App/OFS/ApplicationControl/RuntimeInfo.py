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
__doc__ = """ Runtime Information

$Id: RuntimeInfo.py,v 1.2 2002/06/10 23:27:51 jim Exp $"""

from Zope.App.OFS.ApplicationControl.IRuntimeInfo import IRuntimeInfo
from Zope.App.OFS.ApplicationControl.IApplicationControl import IApplicationControl
from Zope.ComponentArchitecture import getUtility, ComponentLookupError
from IZopeVersion import IZopeVersion
import sys, os, time

class RuntimeInfo:

    __implements__ =  IRuntimeInfo
    __used_for__ = IApplicationControl
    
    def __init__(self, context):
        self.context = context
    
    ############################################################
    # Implementation methods for interface
    # Zope.App.OFS.ApplicationControl.IRuntimeInfo.

    def getZopeVersion(self):
        'See Zope.App.OFS.ApplicationControl.IRuntimeInfo.IRuntimeInfo'
        try:
            version_utility = getUtility(self.context, IZopeVersion)
        except ComponentLookupError:
            return ""
        return version_utility.getZopeVersion()

    def getPythonVersion(self):
        'See Zope.App.OFS.ApplicationControl.IRuntimeInfo.IRuntimeInfo'
        return sys.version

    def getPythonPath(self):
        'See Zope.App.OFS.ApplicationControl.IRuntimeInfo.IRuntimeInfo'
        return tuple(sys.path)

    def getSystemPlatform(self):
        'See Zope.App.OFS.ApplicationControl.IRuntimeInfo.IRuntimeInfo'
        if hasattr(os, "uname"):
            return os.uname()
        else:
            return (sys.platform,)

    def getCommandLine(self):
        'See Zope.App.OFS.ApplicationControl.IRuntimeInfo.IRuntimeInfo'
        return sys.argv

    def getProcessId(self):
        'See Zope.App.OFS.ApplicationControl.IRuntimeInfo.IRuntimeInfo'
        return os.getpid()
    
    def getUptime(self):
        'See Zope.App.OFS.ApplicationControl.IRuntimeInfo.IRuntimeInfo'
        return time.time() - self.context.getStartTime()

    #
    ############################################################
